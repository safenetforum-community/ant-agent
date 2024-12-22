"""
===================================================================================================
Title : agent_quote.py

Description : handler to quote logic

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import inspect
import logging
from log import LogWriter
from dataclasses import dataclass
from client.autonomi import ant_client
from agent.agent_performance import Test
from application import Agent
from agent.agent_limiter import Limiter
import csv 
import os 
import random 
import requests 
import time 
import json
import kill_switch
from agent.agent_helper import Utils
from type_def import typedef_Agent_Client_Response , typedef_Agent_Client_File, typedef_Agent_Performance

cls_agent = Agent()

#logging handler
log_writer = LogWriter()

#get a handle to kill switch detection
killswitch_checker = kill_switch.GitHubRepoIssuesChecker()

#This can go MultiClass, be aware of thread safety !
class AgentQuoter:
    
    def __init__(self):
        #spawn a handler to ant client wrapper
        self.ant_client = ant_client()

        #rate limit handler
        self.rate_limit = Limiter()

# -----> Quote --------------------------------------------------------------
    def Quote (self) -> None:
        
        #todo
        
        del self