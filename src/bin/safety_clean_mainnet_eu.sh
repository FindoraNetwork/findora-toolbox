#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
CONTAINER_NAME=findorad

export ROOT_DIR=/data/findora/${NAMESPACE}

# Fix permissions from possible docker changes
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

##########################################
# Check if container is running and stop #
##########################################
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
wget -O "${ROOT_DIR}/latest" "https://${ENV}-${NAMESPACE}-eu-download.s3.eu-central-1.amazonaws.com/latest"
CHAINDATA_URL=$(cut -d , -f 1 "${ROOT_DIR}/latest")
echo $CHAINDATA_URL

# remove old data 
rm -rf "${ROOT_DIR}/findorad"
rm -rf "${ROOT_DIR}/tendermint/data"
rm -rf "${ROOT_DIR}/tendermint/config/addrbook.json"

wget -O "${ROOT_DIR}/snapshot" "${CHAINDATA_URL}" 
mkdir "${ROOT_DIR}/snapshot_data"
tar zxvf "${ROOT_DIR}/snapshot" -C "${ROOT_DIR}/snapshot_data"

mv "${ROOT_DIR}/snapshot_data/data/ledger" "${ROOT_DIR}/findorad"
mv "${ROOT_DIR}/snapshot_data/data/tendermint/mainnet/node0/data" "${ROOT_DIR}/tendermint/data"

# Fix permissions after download to help startup
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

rm -rf ${ROOT_DIR}/snapshot_data
rm -rf ${ROOT_DIR}/snapshot

######################
# Restart local node #
######################
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

# Wait for the container to be up and the endpoint to respond
while true; do
    # Check if the container is running
    if docker ps --format '{{.Names}}' | grep -Eq '^findorad$'; then
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