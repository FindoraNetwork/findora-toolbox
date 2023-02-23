#!/usr/bin/env bash
set -ex
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
CONTAINER_NAME=findorad

# Fix permissions from possible docker changes
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

##########################################
# Check if container is running and stop #
##########################################
if sudo docker ps -a --format '{{.Names}}' | grep -Eq ${CONTAINER_NAME}; then
  echo -e "Findorad Container found, stopping container to restart."
  sudo docker stop findorad
  sudo docker rm findorad
  rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
  echo 'Findorad container stopped or does not exist, continuing.'
fi

####################
# Wipe Local Files #
####################
sudo rm -r /data/findora/${NAMESPACE}
sudo rm /usr/local/bin/fn
rm ~/.findora.env
