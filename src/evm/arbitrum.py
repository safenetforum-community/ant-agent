"""
===================================================================================================
Title : arbitrum.py

Description : control and interface to the EVM

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

from application import Agent

cls_agent = Agent()

# Notes : This is a single instance class, so ensure that is enforced.
class EvmManager:
    #Ensure this is a single instance class
    _instance = None
    _erc_20_chain = None

    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(EvmManager, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True

    def __set_erc20_chain(self):
        pass

    def __rpc_bind(self):
        pass

    def __get_contract(self):
        pass

    def __get_balance(self):
        pass

    def __set_wallet(self):
        pass

    def __walk_tx_from_tx(self):
        pass

    def __get_token_spend(self):
        pass

    #to-do