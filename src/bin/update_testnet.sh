#!/usr/bin/env bash
set -ex
USERNAME=$USER
ENV=prod
NAMESPACE=testnet
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=fractalfoundation/fractal:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
CONTAINER_NAME=fractal

# Fix permissions from possible docker changes
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

##########################################
# Check if container is running and stop #
##########################################
if docker ps -a --format '{{.Names}}' | grep -Eq ${CONTAINER_NAME}; then
  echo -e "Fractal Container found, stopping container to restart."
  docker stop fractal
  docker rm fractal
  rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
  echo 'Fractal container stopped or does not exist, continuing.'
fi

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
    ${FINDORAD_IMG} node \
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

echo "Local node updated and restarted."