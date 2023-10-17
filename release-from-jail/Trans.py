#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web3
from requests import Timeout
import Config
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename = 'log/release.log', level = logging.INFO)

class Trans:
    def __init__(self):
        config = Config.Config()
        chain = config.getChain()
        operator = config.getOperator()
        self.operator = operator['address']
        self.privateKey = operator['privateKey']
        self.chainId = int(chain['chainId'])
        self.w3 = web3.Web3(web3.HTTPProvider(chain['rpc']))

    def sendTransaction(self, txDict):
        # 获取当前地址交易数
        nonce = self.w3.eth.get_transaction_count(self.operator, 'pending')
        txDict['chainId'] = self.chainId
        txDict['from'] = self.operator
        txDict['nonce'] = nonce
        # 交易签名
        signTx = self.w3.eth.account.signTransaction(txDict, private_key = self.privateKey)
        # 发送交易
        txHash = self.w3.eth.sendRawTransaction(signTx.rawTransaction)
        logger.info('txHash: {}'.format(web3.Web3.toHex(txHash)))

        txReceipt = self.waitReceipt(txHash, 120)  # 默认时间120s
        logger.info('txReceipt: {}'.format(txReceipt))

        if txReceipt.status != 1:
            raise Exception('send transaction error')
        return txReceipt

    # 等待返回结果
    def waitReceipt(self, txHash, maxSeconds):
        try:
            txReceipt = self.w3.eth.waitForTransactionReceipt(txHash, maxSeconds)
        except Timeout:
            raise Timeout('Invoke Contract timeout!')
        return txReceipt