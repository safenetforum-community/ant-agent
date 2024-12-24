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
from type_def import typedef_Agent_Client_Response , typedef_Agent_Client_File, typedef_Agent_Performance, typedef_Agent_Quoter

cls_agent = Agent()

#logging handler
log_writer = LogWriter()

#get a handle to kill switch detection
killswitch_checker = kill_switch.GitHubRepoIssuesChecker()

CONST_QUOTE_PATH = "./cache/quote/"

#This can go MultiClass, be aware of thread safety !
class AgentQuoter:
    
    def __init__(self):
        #spawn a handler to ant client wrapper
        self.ant_client = ant_client()

        #rate limit handler
        self.rate_limit = Limiter()
   
#-----> Cache handling of files that can be processed in the CSV file ----------------------------------------
    def __download_quote_csv(self): 
        response = requests.get(cls_agent.Configuration.CSV_QUOTE_URL) 
        response.raise_for_status() 
        with open(cls_agent.Configuration.CACHE_QUOTE_FILE, 'w', newline='') as file: 
            file.write(response.text) 
        with open(cls_agent.Configuration.CACHE_QUOTE_META, 'w') as info_file: 
            cache_info = {'download_time': time.time()} 
            json.dump(cache_info, info_file) 
                
    def __is_quote_cache_valid(self): 
        if os.path.exists(cls_agent.Configuration.CACHE_QUOTE_META) and os.path.exists(cls_agent.Configuration.CACHE_QUOTE_FILE): 
            with open(cls_agent.Configuration.CACHE_QUOTE_META, 'r') as info_file: 
                cache_info = json.load(info_file) 
                if time.time() - cache_info['download_time'] < cls_agent.Configuration.CACHE_TIME: 
                    return True
                #endIf 
                return False 
            #endWith
        #endIf

    def del_quote_file(self,filename): 
        try: #todo
            os.remove(filename) 
            log_writer.log(f"File '{filename}' has been deleted successfully.",logging.DEBUG) 
        except FileNotFoundError: 
            log_writer.log(f"File '{filename}' not found.",logging.DEBUG) 
        except PermissionError: 
            log_writer.log(f"Permission denied: Unable to delete file '{filename}'.",logging.DEBUG) 
        except Exception as e: 
            log_writer.log(f"Error: {e} occurred while trying to delete file '{filename}'.",logging.ERROR) 
        
    def get_quote_file(self,_filesize) -> str: 
        if not self.__is_quote_cache_valid(): 
            self.__download_quote_csv()
        #endIf
            
        with open(cls_agent.Configuration.CACHE_QUOTE_FILE, newline='') as csvfile: 
            reader = csv.DictReader(row for row in csvfile if not row.startswith('#')) 
            matching_rows = [row for row in reader if row.get('fileSize') == _filesize] 
            if matching_rows: 
                _row = random.choice(matching_rows)
                _, seed, size, _ = _row
                seed = int(_row['seed'])
                size = int(_row['size'])
                generator = QuoteFileGenerator(seed)
                filename = os.path.join(CONST_QUOTE_PATH,f"{_filesize}_{uuid.uuid4().hex}.bin")  #todo: needs config for path
                if not os.path.exists(CONST_QUOTE_PATH): 
                    os.makedirs(CONST_QUOTE_PATH) 

                with open(filename, 'wb') as f:
                    remaining_bytes = size
                    while remaining_bytes > 0:
                        chunk = min(remaining_bytes, 1024)
                        f.write(generator.randbytes(chunk))
                        remaining_bytes -= chunk
                log_writer.log(f"File {filename} created with size {size} bytes.",logging.DEBUG)
                return filename
            else: 
                return None
            #endIf
        #endWith
    
# -----> Quote --------------------------------------------------------------
    def quote (self, _quote : typedef_Agent_Quoter) -> None:
        
        #todo
        log_writer.log(f"AgentQuoter:quote: Start | filesize:{_quote.filesize} | Repeating:{_quote.repeat} | Offset :{_quote.offset}",logging.DEBUG)

        # ensure we go through one itteration
        repeat_loop = True  

        #python type casting on how it handles boolean =o
        #todo: need to handle that when passing XML input file, this is the wrong place as we will be duplicating
        repeat = _quote.repeat.lower() in ['true', '1', 'yes']

        if _quote.offset in ('false','0','no'): 
            _quote.offset = 0
        else:
            _quote.offset = int(_quote.offset)
            if _quote.offset > cls_agent.Configuration.CLIENT_MAX_OFFSET:
                _quote.offset = cls_agent.Configuration.CLIENT_MAX_OFFSET
            #endIf
        #endIf

        if _quote.filesize:
            _filesize = _quote.filesize
        else:
            _filesize = "medium"
        #endIfElse

        _quote_filename = self.get_quote_file(_filesize)

        # Mimicking do-while loop :(
        while repeat_loop: 
            #*** Start Quote

            #push into rate limiter, on true we are overloaded so break
            rl = self.rate_limit.is_ratelimit_quote()
            if rl:
                break

            #start a performance instance
            _quote_results = typedef_Agent_Performance()
            _quote_results.test_type = "quote"
            _quote_results.filesize = _quote.filesize

            if _quote_filename:
                if isinstance(_quote.offset, int) and int(_quote.offset) > 0:
                    #call the offset, and sleep for this long
                    time_to_sleep = Utils.offset(offset_minutes=int(_quote.offset))
                    log_writer.log(f"AgentQuoter.quote: offset is set | time_to_sleep {time_to_sleep}", logging.DEBUG)
                    time.sleep(time_to_sleep)
                #endIf

                #push our test instance, into a test we are about to run
                _performance = Test()
                _response = typedef_Agent_Client_Response() 

                #push timer start
                _performance.start_timer()
                
                try:
                    #custom type for client response handling - strong typing needed #todo fix timeout
                    _response: typedef_Agent_Client_Response = self.ant_client.quote (_quote_filename,_quote.timeout)
                except Exception as e:
                    #to:do need to fill in _response
                    _response.client_error = True
                    _response.client_started = True

                _performance.stop_timer()
                #end timer              

                # Generate the list of fields dynamically from _quote_results
                _fields = vars(_quote_results).keys()

                # Map values from _response to _download_results
                for _field in _fields:
                    if hasattr(_response, _field):
                        setattr(_quote_results, _field, getattr(_response, _field))

                    
                # Push results to performance class
                _performance.add_results(_quote_results)
       
            else: 
                #need to handle this somehow...
                log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: Error getting Quote file for {_quote.filesize}",logging.ERROR)

                #throw and exception, as we can't run this task
                #to-do: need a more graceful way to just block download tasks
                cls_agent.Exception.throw(error="AgentQuoter.quote: Unable to find a quote file for select filesize")
            #endIfElse

            #*** Finish Quote
            # Update condition if we have been requested to loop
            if bool(repeat):
                #check to see if we should be cancelling due to kill switch
                if killswitch_checker.check_for_kill_switch()[0]: #need a try catch in the kill switch class
                    repeat_loop = False
                    break
                elif Utils.scheduler_no_tasks_window():
                    repeat_loop = False
                    break
                #endIfElse

                #enfore a sleep, so this thread can yield
                time.sleep(cls_agent.Configuration.QUOTE_YIELD_SECS)                 
            else:
                #quote was not requested to repeat
                repeat_loop = False
            #endIf
        #endWhile

        self.del_quote_file(_quote_filename)

        log_writer.log(f"AgentQuoter.quote: Finished",logging.DEBUG)

        del self

#todo: needs flushing out and made consistent over different CPU architectures
class QuoteFileGenerator:
    def __init__(self, seed):
        self.seed = seed

    def _set_seed(self):
        random.seed(self.seed)

    def randbytes(self, n):
        self._set_seed()
        return random.randbytes(n)