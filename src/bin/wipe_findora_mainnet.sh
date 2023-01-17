#!/usr/bin/env bash
set -ex
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
CONTAINER_NAME=findorad

# Reset permissions to avoid problems.
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}

###################
# Stop local node #
###################
if docker ps -a --format '{{.Names}}' | grep -Eq ${CONTAINER_NAME}; then
  echo -e "Findorad Container found, stopping container to restart."
  docker stop findorad
  docker rm findorad 
  rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
  echo 'Findorad container stopped or does not exist, continuing.'
fi

sudo rm -r /data/findora/${NAMESPACE}
sudo rm /usr/local/bin/fn
rm ~/.easynode.env
