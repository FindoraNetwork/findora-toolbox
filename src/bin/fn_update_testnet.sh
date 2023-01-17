#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=testnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
export ROOT_DIR=/data/findora/${NAMESPACE}
FN=${ROOT_DIR}/bin/fn

##################
# Install fn App #
##################
wget https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn
chmod +x fn
sudo mv fn /usr/local/bin/

$FN setup -S ${SERV_URL} || exit 1
$FN setup -K ${ROOT_DIR}/tendermint/config/priv_validator_key.json || exit 1
$FN setup -O ${ROOT_DIR}/node.mnemonic || exit 1