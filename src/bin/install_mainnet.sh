#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=fractalfoundation/fractal:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
keypath=${ROOT_DIR}/${NAMESPACE}_node.key
CONTAINER_NAME=fractal

check_env() {
    for i in wget curl; do
        which $i >/dev/null 2>&1
        if [[ 0 -ne $? ]]; then
            echo -e "\n\033[31;01m${i}\033[00m has not been installed properly!\n"
            exit 1
        fi
    done
    
    if ! [ -f "$keypath" ]; then
        echo -e "No tmp.gen.keypair file detected, generating file and creating to ${NAMESPACE}_node.key"
        fn genkey > /tmp/tmp.gen.keypair
    fi
}

##################
# Install fn App #
##################
wget https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn
chmod +x fn
sudo mv fn /usr/local/bin/

######################################
# Make Directories & Set Permissions #
######################################
sudo mkdir -p /data/findora
mkdir -p /home/${USERNAME}/findora_backup
sudo chown -R ${USERNAME}:${USERNAME} /data/findora/
mkdir -p /data/findora/${NAMESPACE}

############################
# Check for existing files #
############################
check_env

cp /tmp/tmp.gen.keypair /home/${USERNAME}/findora_backup/tmp.gen.keypair
mv /tmp/tmp.gen.keypair /data/findora/${NAMESPACE}/${NAMESPACE}_node.key

#####################
# Config local node #
#####################
node_mnemonic=$(cat ${keypath} | grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //')

echo $node_mnemonic > ${ROOT_DIR}/node.mnemonic || exit 1
cp ${ROOT_DIR}/node.mnemonic /home/${USERNAME}/findora_backup/node.mnemonic

fn setup -S ${SERV_URL} || exit 1
fn setup -K ${ROOT_DIR}/tendermint/config/priv_validator_key.json || exit 1
fn setup -O ${ROOT_DIR}/node.mnemonic || exit 1

# clean old data and config files
sudo rm -rf ${ROOT_DIR}/${NAMESPACE} || exit 1
mkdir -p ${ROOT_DIR}/${NAMESPACE} || exit 1

# tendermint config
docker run --rm -v ${ROOT_DIR}/tendermint:/root/.tendermint ${FINDORAD_IMG} init --${NAMESPACE} || exit 1

# reset permissions on tendermint folder after init
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}/tendermint

# backup priv_validator_key.json
cp -a ${ROOT_DIR}/tendermint/config /home/${USERNAME}/findora_backup/config

# if you're re-running this for some reason, stop and remove fractal
if docker ps -a --format '{{.Names}}' | grep -Eq ${CONTAINER_NAME}; then
    echo -e "Fractal Container found, stopping container to restart."
    docker stop fractal
    docker rm fractal
    rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
    echo 'Fractal container stopped or does not exist, continuing.'
fi

###################
# get snapshot    #
###################

# download latest link and get url
wget -O "${ROOT_DIR}/latest" "https://${ENV}-${NAMESPACE}-us-west-2-chain-data-backup.s3.us-west-2.amazonaws.com/latest"
CHAINDATA_URL=$(cut -d , -f 1 "${ROOT_DIR}/latest")
CHECKSUM_LATEST=$(cut -d , -f 2 "${ROOT_DIR}/latest")
echo $CHAINDATA_URL

# remove old data
rm -rf "${ROOT_DIR}/fractal"
rm -rf "${ROOT_DIR}/tendermint/data"
rm -rf "${ROOT_DIR}/tendermint/config/addrbook.json"

# check snapshot file md5sum
while :
do
    echo "Downloading snapshot..."
    wget --progress=bar:force -O "${ROOT_DIR}/snapshot" "${CHAINDATA_URL}" || { echo "Failed to download snapshot."; exit 1; }
    CHECKSUM=$(md5sum "${ROOT_DIR}/snapshot" | cut -d " " -f 1)
    if [[ ! -z "$CHECKSUM_LATEST" ]] && [[ "$CHECKSUM_LATEST" = "$CHECKSUM" ]]; then
        break
    fi
done

# Define the directory paths
SNAPSHOT_DIR="${ROOT_DIR}/snapshot_data"
LEDGER_DIR="${ROOT_DIR}/fractal"
TENDERMINT_DIR="${ROOT_DIR}/tendermint/data"

# Create the snapshot directory
mkdir "$SNAPSHOT_DIR"

# Extract the tar archive and check the exit status
echo "Extracting snapshot and setting up the local node..."
if ! pv "${ROOT_DIR}/snapshot" | tar zxvf - -C "$SNAPSHOT_DIR" > /dev/null; then
    echo "Error: Failed to extract the snapshot. Please check if there is enough disk space and permissions."
    exit 1
fi

# Move the extracted files to the desired locations
mv "${SNAPSHOT_DIR}/data/ledger" "$LEDGER_DIR"
mv "${SNAPSHOT_DIR}/data/tendermint/mainnet/node0/data" "$TENDERMINT_DIR"

# Remove the temporary directories and files
rm -rf "$SNAPSHOT_DIR"
rm -rf "${ROOT_DIR}/snapshot"

#####################
# Create local node #
#####################
docker run -d \
-v ${ROOT_DIR}/tendermint:/root/.tendermint \
-v ${ROOT_DIR}/fractal:/tmp/findora \
-p 8669:8669 \
-p 8668:8668 \
-p 8667:8667 \
-p 8545:8545 \
-p 26657:26657 \
-e EVM_CHAIN_ID=2152 \
--name fractal \
${FINDORAD_IMG} node \
--ledger-dir /tmp/findora \
--tendermint-host 0.0.0.0 \
--tendermint-node-key-config-path="/root/.tendermint/config/priv_validator_key.json" \

# Wait for the container to be up and the endpoint to respond
while true; do
    # Check if the container is running
    if docker ps --format '{{.Names}}' | grep -Eq '^fractal$'; then
        # Check the response from the curl endpoint
        if curl -s 'http://localhost:26657/status' > /dev/null; then
            echo "Container is up and endpoint is responding."
            break
        else
            echo "Container is up, but endpoint is not responding yet. Retrying in 10 seconds..."
            sleep 10
        fi
    else
        echo "Container is not running. Exiting..."
        exit 1
    fi
done

#############################
# Post Install Stats Report #
#############################
curl 'http://localhost:26657/status'; echo
curl 'http://localhost:8669/version'; echo
curl 'http://localhost:8668/version'; echo
curl 'http://localhost:8667/version'; echo

echo "Local node initialized! You can now run the migration process or wait for sync and create your validator."