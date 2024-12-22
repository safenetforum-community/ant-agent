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
import csv
import random
import uuid
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

#todo: needs flushing out
class QuoteFileGenerator:
    def __init__(self, seed):
        self.seed = seed

    def _set_seed(self):
        random.seed(self.seed)

    def randbytes(self, n):
        self._set_seed()
        return random.randbytes(n)

    def generate_file_from_csv(csv_filename, file_size):
        with open(csv_filename, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip the header
            for row in reader:
                if row[0].startswith('#'):  # Ignore lines starting with #
                    continue
                if row[0] == file_size:
                    _, seed, size, _ = row
                    seed = int(seed)
                    size = int(size)
                    generator = QuoteFileGenerator(seed)
                    filename = f"{file_size}_{uuid.uuid4().hex}.bin"  #todo: needs config for path
                    with open(filename, 'wb') as f:
                        remaining_bytes = size
                        while remaining_bytes > 0:
                            chunk = min(remaining_bytes, 1024)
                            f.write(generator.randbytes(chunk))
                            remaining_bytes -= chunk
                    log_writer.log(f"File {filename} created with size {size} bytes.",logging.DEBUG)
                    return
            log_writer.log(f"No matching file size found for: {file_size}",logging.DEBUG)