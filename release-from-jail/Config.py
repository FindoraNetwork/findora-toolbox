#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('properties.conf')

    def getChain(self):
        return self.config['chain']

    def getContract(self):
        return self.config['contract']
    
    def getOperator(self):
        return self.config['operator']
    
    def getNode(self):
        return self.config['node']
