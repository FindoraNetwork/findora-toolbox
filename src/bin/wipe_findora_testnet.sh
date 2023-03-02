#!/usr/bin/env bash
set -ex
USERNAME=$USER
ENV=prod
NAMESPACE=testnet
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
CONTAINER_NAME=findorad

# Fix permissions from possible docker changes
if [ -d ${ROOT_DIR} ]; then
  sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}
fi

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

####################
# Wipe Local Files #
####################
if [ -d /data/findora/${NAMESPACE} ]; then
  sudo rm -r /data/findora/${NAMESPACE}
fi
sudo rm /usr/local/bin/fn
rm ~/.findora.env
