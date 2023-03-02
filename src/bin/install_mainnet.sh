#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
keypath=${ROOT_DIR}/${NAMESPACE}_node.key
FN=${ROOT_DIR}/bin/fn
CONTAINER_NAME=findorad

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

set_binaries() {
    # OS=$1
    docker pull ${FINDORAD_IMG} || exit 1
    wget -T 10 https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn || exit 1

    new_path=${ROOT_DIR}/bin

    rm -rf $new_path 2>/dev/null
    mkdir -p $new_path || exit 1
    mv fn $new_path || exit 1
    chmod -R +x ${new_path} || exit 1
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

if [[ "Linux" == `uname -s` ]]; then
    set_binaries linux
# elif [[ "FreeBSD" == `uname -s` ]]; then
    # set_binaries freebsd
elif [[ "Darwin" == `uname -s` ]]; then
    set_binaries macos
else
    echo "Unsupported system platform!"
    exit 1
fi

#####################
# Config local node #
#####################
node_mnemonic=$(cat ${keypath} | grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //')
xfr_pubkey="$(cat ${keypath} | grep 'pub_key' | sed 's/[",]//g' | sed 's/ *pub_key: *//')"

echo $node_mnemonic > ${ROOT_DIR}/node.mnemonic || exit 1
cp ${ROOT_DIR}/node.mnemonic /home/${USERNAME}/findora_backup/node.mnemonic

$FN setup -S ${SERV_URL} || exit 1
$FN setup -K ${ROOT_DIR}/tendermint/config/priv_validator_key.json || exit 1
$FN setup -O ${ROOT_DIR}/node.mnemonic || exit 1

# clean old data and config files
sudo rm -rf ${ROOT_DIR}/${NAMESPACE} || exit 1
mkdir -p ${ROOT_DIR}/${NAMESPACE} || exit 1


# tendermint config
docker run --rm -v ${ROOT_DIR}/tendermint:/root/.tendermint ${FINDORAD_IMG} init --${NAMESPACE} || exit 1

# reset permissions on tendermint folder after init
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}/tendermint

# backup priv_validator_key.json
cp -a ${ROOT_DIR}/tendermint/config /home/${USERNAME}/findora_backup/config

# if you're re-running this for some reason, stop and remove findorad
if docker ps -a --format '{{.Names}}' | grep -Eq ${CONTAINER_NAME}; then
  echo -e "Findorad Container found, stopping container to restart."
  docker stop findorad
  docker rm findorad
  rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
  echo 'Findorad container stopped or does not exist, continuing.'
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
rm -rf "${ROOT_DIR}/findorad"
rm -rf "${ROOT_DIR}/tendermint/data"
rm -rf "${ROOT_DIR}/tendermint/config/addrbook.json"

# check snapshot file md5sum
while :
do
    wget -O "${ROOT_DIR}/snapshot" "${CHAINDATA_URL}"
    CHECKSUM=$(md5sum "${ROOT_DIR}/snapshot" | cut -d " " -f 1)
    if [[ ! -z "$CHECKSUM_LATEST" ]] && [[ "$CHECKSUM_LATEST" = "$CHECKSUM" ]]; then
        break
    fi
done

mkdir "${ROOT_DIR}/snapshot_data"
tar zxvf "${ROOT_DIR}/snapshot" -C "${ROOT_DIR}/snapshot_data"

mv "${ROOT_DIR}/snapshot_data/data/ledger" "${ROOT_DIR}/findorad"
mv "${ROOT_DIR}/snapshot_data/data/tendermint/mainnet/node0/data" "${ROOT_DIR}/tendermint/data"

rm -rf ${ROOT_DIR}/snapshot_data
rm -rf ${ROOT_DIR}/snapshot

#####################
# Create local node #
#####################
docker run -d \
    -v ${ROOT_DIR}/tendermint:/root/.tendermint \
    -v ${ROOT_DIR}/findorad:/tmp/findora \
    -p 8669:8669 \
    -p 8668:8668 \
    -p 8667:8667 \
    -p 8545:8545 \
    -p 26657:26657 \
    -e EVM_CHAIN_ID=2152 \
    --name findorad \
    ${FINDORAD_IMG} node \
    --ledger-dir /tmp/findora \
    --tendermint-host 0.0.0.0 \
    --tendermint-node-key-config-path="/root/.tendermint/config/priv_validator_key.json" \
    --enable-query-service \
    --enable-eth-api-service

sleep 10

#############################
# Post Install Stats Report #
#############################
curl 'http://localhost:26657/status'; echo
curl 'http://localhost:8669/version'; echo
curl 'http://localhost:8668/version'; echo
curl 'http://localhost:8667/version'; echo

echo "Local node initialized, please stake your FRA tokens after syncing is completed."