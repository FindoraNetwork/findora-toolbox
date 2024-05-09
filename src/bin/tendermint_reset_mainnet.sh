#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=fractalfoundation/fractal:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
keypath=${ROOT_DIR}/${NAMESPACE}_node.key
FN=${ROOT_DIR}/bin/fn
CONTAINER_NAME=fractal

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

docker run --rm -v ${ROOT_DIR}/tendermint:/root/.tendermint ${FINDORAD_IMG} init --${NAMESPACE} || exit 1

echo -e "* Tendermint has been reconfigured, run the update_version script or option to get back online."