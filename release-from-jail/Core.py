#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import web3
import time
from datetime import datetime
import Config
import Trans
import requests
    
class Core:

    def __init__(self):
        config = Config.Config()
        chain = config.getChain()
        contract = config.getContract()
        node = config.getNode()
        self.stakingAddr = contract['staking']
        self.validatorAddr = node['validator']
        self.nodeUrl = node['url']
        self.w3 = web3.Web3(web3.HTTPProvider(chain['rpc']))
    
    def getContract(self):
        stakingAddr = self.w3.toChecksumAddress(self.stakingAddr)
        abiFile = os.path.join(os.getcwd(), 'abis/Staking.json')
        with open(abiFile) as json_file:
            abiJson = json.loads(json_file.read())
        # 获取ABI
        contract_abi = abiJson['abi']
        # 返回合约
        return self.w3.eth.contract(abi = contract_abi, address = stakingAddr)
        
    def getStatus(self, validator):
        result = self.getContract().functions.validatorStatus(validator).call()
        return result
    
    def releaseFromJail(self):
        validatorAddr = self.w3.toChecksumAddress(self.validatorAddr)
        if(self.checkRelease(validatorAddr)):
            gasPrice = self.w3.eth.gasPrice
            txnDict = self.getContract().functions.releaseFromJail(validatorAddr).buildTransaction({
                'gas': 400000,
                'gasPrice': gasPrice,
            })
            Trans.Trans().sendTransaction(txnDict)

    def checkRelease(self, validatorAddr):
        validatorStatus = self.getStatus(validatorAddr)
        if(validatorStatus is None):
            print('notice: invalid validator')
            return False
        
        if(validatorStatus[2] == False):
            print('notice: validator is not jailed')
            return False
        
        current_timestamp = int(time.time())
        if(validatorStatus[3] > current_timestamp):
            current_datetime = datetime.fromtimestamp(current_timestamp)
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            print('notice: release time is: {}'.format(formatted_datetime))
            return False
        
        if(self.getPrivateNodeStatus()):
            print('notice: validator synchronization error')
            return False
        
        return True

    def getPrivateNodeStatus(self):
        response = requests.get(self.nodeUrl)
        if response.status_code == 200:
            # Request was successful
            data = response.json()  # Assuming the response contains JSON data
            return data["result"]["sync_info"]["catching_up"]
        else:
            # Request failed
            print('Request failed with status code:', response.status_code)

        return True


