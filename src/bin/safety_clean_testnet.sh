#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=testnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FRACTAL_IMG=fractalfoundation/fractal:${LIVE_VERSION}
CHECKPOINT_URL=https://${ENV}-${NAMESPACE}-us-west-2-ec2-instance.s3.us-west-2.amazonaws.com/${NAMESPACE}/checkpoint
CONTAINER_NAME=fractal

export ROOT_DIR=/data/findora/${NAMESPACE}

# Fix permissions from possible docker changes
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

##########################################
# Check if container is running and stop #
##########################################
if docker ps -a --format '{{.Names}}' | grep -Eq findorad; then
    echo -e "Findorad Container found, stopping container to restart."
    docker stop findorad
    docker rm findorad
    rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
fi

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

rm -rf "${ROOT_DIR}/findora"
rm -rf "${ROOT_DIR}/findorad"
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
LEDGER_DIR="${ROOT_DIR}/findorad"
TENDERMINT_DIR="${ROOT_DIR}/tendermint/data"

# Create the snapshot directory
mkdir "$SNAPSHOT_DIR"

# Get the available disk space before extraction
AVAILABLE_SPACE_BEFORE=$(df --output=avail "$SNAPSHOT_DIR" | tail -n 1)

# Extract the tar archive and check the exit status
echo "Extracting snapshot and setting up the local node..."
if ! tar zxvf "${ROOT_DIR}/snapshot" -C "$SNAPSHOT_DIR" > /dev/null 2>&1; then
    echo "Error: Failed to extract the snapshot. Please check if there is enough disk space and permissions."
    exit 1
fi

# Get the available disk space after extraction
AVAILABLE_SPACE_AFTER=$(df --output=avail "$SNAPSHOT_DIR" | tail -n 1)

# Check if the available disk space is less than expected
if (( AVAILABLE_SPACE_AFTER >= AVAILABLE_SPACE_BEFORE )); then
    echo "Error: Disk space is full. Please free up some space and try again."
    rm -rf "$SNAPSHOT_DIR"
    exit 1
fi

# Move the extracted files to the desired locations
mv "${SNAPSHOT_DIR}/data/ledger" "$LEDGER_DIR"
mv "${SNAPSHOT_DIR}/data/tendermint/mainnet/node0/data" "$TENDERMINT_DIR"

# Remove the temporary directories and files
rm -rf "$SNAPSHOT_DIR"
rm -rf "${ROOT_DIR}/snapshot"

###################
# Get checkpoint  #
###################
rm -rf "${ROOT_DIR}/checkpoint.toml"
wget -O "${ROOT_DIR}/checkpoint.toml" "${CHECKPOINT_URL}"

######################
# Restart local node #
######################
docker run -d \
    -v ${ROOT_DIR}/tendermint:/root/.tendermint \
    -v ${ROOT_DIR}/findora:/tmp/findora \
    -v ${ROOT_DIR}/checkpoint.toml:/root/checkpoint.toml \
    -p 8669:8669 \
    -p 8668:8668 \
    -p 8667:8667 \
    -p 8545:8545 \
    -p 26657:26657 \
    -e EVM_CHAIN_ID=2153 \
    --name fractal \
    ${FRACTAL_IMG} node \
    --ledger-dir /tmp/findora \
    --checkpoint-file=/root/checkpoint.toml \
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

echo "Local node data wiped, reloaded, container updated and restarted."