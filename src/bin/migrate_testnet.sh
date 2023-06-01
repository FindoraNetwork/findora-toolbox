#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=testnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
LIVE_VERSION=$(curl -s https://${ENV}-${NAMESPACE}.${ENV}.findora.org:8668/version | awk -F\  '{print $2}')
FINDORAD_IMG=findoranetwork/findorad:${LIVE_VERSION}
export ROOT_DIR=/data/findora/${NAMESPACE}
keypath=${ROOT_DIR}/${NAMESPACE}_node.key
migratepath=/home/${USERNAME}/migrate
FN=${ROOT_DIR}/bin/fn
container_name=findorad

check_env() {
    for i in wget curl; do
        which $i >/dev/null 2>&1
        if [[ 0 -ne $? ]]; then
            echo -e "\n\033[31;01m${i}\033[00m has not been installed properly!\n"
            exit 1
        fi
    done

    if [ -d "$migratepath" ]; then
        echo -e "Migrate folder found, preparing to copy files..."
    else
        echo -e "Create the folder ~/migrate with your node.mnemonic, priv_validator_key.json and tmp.gen.keypair files to continue."
        exit 1
    fi

    if [ -f "$migratepath/tmp.gen.keypair" ]; then
        cp ${migratepath}/tmp.gen.keypair ${ROOT_DIR}/${NAMESPACE}_node.key
    else
        echo -e "tmp.gen.keypair file not found at ~/migrate/tmp.gen.keypair - Add this file to ~/migrate to continue."
        exit 1
    fi

    if [ -f "$migratepath/config" ]; then
        echo -e "~/migrate/config found, copying."
        cp ${migratepath}/config/* ${ROOT_DIR}/tendermint/config/
    elif ! ["$migratepath/priv_validator_key.json"]; then
        echo -e "~/migrate/priv_validator_key.json found, copying."
        cp ${migratepath}/priv_validator_key.json ${ROOT_DIR}/tendermint/config/priv_validator_key.json
    else
        echo -e "No config folder or priv_validator_key.json file found in ~/migrate. Please add these files to continue."
        exit 1
    fi

    if [ -f "$migratepath/node.mnemonic" ]; then
        cp ${migratepath}/node.mnemonic ${ROOT_DIR}/node.mnemonic
    else
        echo -e "node.mnemonic not found at ~/migrate/node.mnemonic - Creating from ~/migrate/tmp.gen.keypair file."
        node_mnemonic=$(cat ${keypath} | grep 'Mnemonic' | sed 's/^.*Mnemonic:[^ ]* //')
        echo $node_mnemonic > ${ROOT_DIR}/node.mnemonic || exit 1
    fi
}

##########################################
# Check if container is running and stop #
##########################################
if docker ps -a --format '{{.Names}}' | grep -Eq "^${container_name}\$"; then
  echo -e "Findorad Container found, stopping container."
  docker stop findorad
  docker rm findorad
  rm -rf /data/findora/mainnet/tendermint/config/addrbook.json
else
  echo 'Findorad container stopped or does not exist, continuing.'
fi

check_env

###########################
# Re-configure local node #
###########################
$FN setup -S ${SERV_URL} || exit 1
$FN setup -K ${ROOT_DIR}/tendermint/config/priv_validator_key.json || exit 1
$FN setup -O ${ROOT_DIR}/node.mnemonic || exit 1

docker run --rm -v ${ROOT_DIR}/tendermint:/root/.tendermint ${FINDORAD_IMG} init --${NAMESPACE} || exit 1

# reset permissions on tendermint folder after init
sudo chown -R ${USERNAME}:${USERNAME} ${ROOT_DIR}/tendermint

###################
# Run local node  #
###################
docker run -d \
    -v ${ROOT_DIR}/tendermint:/root/.tendermint \
    -v ${ROOT_DIR}/findorad:/tmp/findora \
    -v ${ROOT_DIR}/checkpoint.toml:/root/checkpoint.toml \
    -p 8669:8669 \
    -p 8668:8668 \
    -p 8667:8667 \
    -p 8545:8545 \
    -p 26657:26657 \
    -e EVM_CHAIN_ID=2153 \
    --name findorad \
    ${FINDORAD_IMG} node \
    --ledger-dir /tmp/findora \
    --checkpoint-file=/root/checkpoint.toml \
    --tendermint-host 0.0.0.0 \
    --tendermint-node-key-config-path="/root/.tendermint/config/priv_validator_key.json" \
    --enable-query-service \

sleep 30

curl 'http://localhost:26657/status'; echo
curl 'http://localhost:8669/version'; echo
curl 'http://localhost:8668/version'; echo
curl 'http://localhost:8667/version'; echo

echo "Local node migrated."