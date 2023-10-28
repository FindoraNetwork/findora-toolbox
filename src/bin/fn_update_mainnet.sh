#!/usr/bin/env bash
USERNAME=$USER
ENV=prod
NAMESPACE=mainnet
SERV_URL=https://${ENV}-${NAMESPACE}.${ENV}.findora.org
export ROOT_DIR=/data/findora/${NAMESPACE}
FN=${ROOT_DIR}/bin/fn

##################
# Install fn App #
##################

# Downloading
echo -n "Downloading ..."
wget -O fn https://github.com/FindoraNetwork/findora-wiki-docs/raw/main/.gitbook/assets/fn >/dev/null 2>&1
echo " completed"

# Setting permissions
chmod +x fn

# Copying
echo -n "Copying ..."
sudo mv fn /usr/local/bin/ >/dev/null 2>&1
cp /usr/local/bin/fn $FN >/dev/null 2>&1
echo " completed"

# Configuring
echo -n "Configuring ..."
$FN setup -S ${SERV_URL} >/dev/null 2>&1 || { echo " failed"; exit 1; }
$FN setup -K ${ROOT_DIR}/tendermint/config/priv_validator_key.json >/dev/null 2>&1 || { echo " failed"; exit 1; }
$FN setup -O ${ROOT_DIR}/node.mnemonic >/dev/null 2>&1 || { echo " failed"; exit 1; }
echo " completed"
