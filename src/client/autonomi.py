"""
===================================================================================================
Title : autonomi.py

Description : Wrapper around binaries

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import subprocess
import shutil
import os
import threading
import tempfile
import inspect
import logging
import string
import random
import time
import hashlib
from log import LogWriter
from application import Agent
from type_def import typedef_Agent_Client_Response, typedef_Agent_Client_File
from client import autonomi_messages

cls_agent = Agent()
log_writer = LogWriter()

class ant_client:
   process : subprocess.Popen = None

   def ___init___(self):
      # BOILER: todo
      pass

   def __del__(self):
      #todo: wrong place
      log_writer.log(f"Ant_Client:Wrapper: Finished",logging.DEBUG)

   def _generate_random_alphanumeric(self): 
      #todo
      # Define the set of possible characters: digits and letters (both uppercase and lowercase) 
      characters = string.ascii_letters + string.digits 
      
      # Use random.choices to select 3 random characters from the set 
      random_string = ''.join(random.choices(characters, k=3)) 
      
      return random_string    

   def __start_watchdog(self):
        try:
            _self_thread_name = threading.current_thread().name

            if _self_thread_name:
                self._stop_watchdog = threading.Event()
                self._watchdog = threading.Thread(target=self.__run_watchdog, name=f"{_self_thread_name}.{self._generate_random_alphanumeric()}_watchdog")
                self._watchdog.start()
            #endIf
        except Exception as e:
            #to-do: throwing exception, but this needs better handling of why on __init__
            cls_agent.Exception.throw(error=(f"ant_client.__start_watchdog: {e}"))
        #endTry

   def __run_watchdog(self):
        log_writer.log(f"ant_client.__run_watchdog: Watchdog thread started",logging.DEBUG)
        
        while not self._stop_watchdog.is_set():
            if cls_agent.is_Agent_Shutdown() or cls_agent.is_Threads_Terminate_Requested():
                self._stop_watchdog.set()
            time.sleep(1)
        #endWhile

        log_writer.log(f"ant_client.__run_watchdog: Watchdog thread exited, killing class",logging.DEBUG)

        self.terminate()

   def terminate(self):
         log_writer.log(f"ant_client.Terminate: Deleting Self", logging.DEBUG)
        
         if self.process.poll() is None:
            self.process.kill()
            time.sleep(20) #provide time for results to be processed
         #endIf

         del self    
   
   def __get_temp_filepath (self,filename):
      if filename:
         prefix = filename.lower()
      else:
         prefix ="unknown"

      temp_file_name = os.path.join( cls_agent.Configuration.CLIENT_DOWNLOAD_PATH, f"{prefix}_{next(tempfile._get_candidate_names())}" )
      return (temp_file_name)
   
   def __del_temp_filepath(self, filepath): 
      try: 
         if os.path.exists(filepath): 
            if os.path.isfile(filepath): 
               os.remove(filepath) 
            elif os.path.isdir(filepath): 
               shutil.rmtree(filepath) 
            #endIfElse
         #endIf
      except Exception as e: 
         log_writer.log(f"ant_client.__del_temp_filepath: Error occurred while deleting {filepath}: {e}",logging.DEBUG)
   
   def __get_single_filename(self, directory): 
      try: 
         files = os.listdir(directory) 
         if len(files) == 1: 
            return files[0] 
         else: 
            return None 
      except Exception as e: 
         log_writer.log(f"ant_client.__get_single_filename: No File Found {directory}", logging.DEBUG) 
      return None

   def quote(self, filename, timeout=30) -> typedef_Agent_Client_Response:

      self.__start_watchdog()

      _return_results : typedef_Agent_Client_Response = typedef_Agent_Client_Response()
      _stderr_break = False

       # BOILER: todo
      log_writer.log(f"ant_client:quote: Start | file: {filename}",logging.DEBUG) 

      temp_file_name_log = cls_agent.Configuration.CLIENT_LOGGING_PATH
            
      #pass custom peers from environment
      if cls_agent.Configuration.CLIENT_PEERS:
         command = [ 
            './bin/ant', 
            '--peer', str(cls_agent.Configuration.CLIENT_PEERS),
            '--timeout', str(timeout),
            '--ignore-cache',
            '--log-output-dest', 
            temp_file_name_log, 
            'file', 
            'cost', 
            filename
         ]
      else:
         command = [ 
            './bin/ant', 
            '--timeout', str(timeout), 
            '--ignore-cache',
            '--log-output-dest', 
            temp_file_name_log, 
            'file', 
            'cost',
            filename 
         ]
      #endIf

      try:
         #needs wrapping in a timer

         _return_results.client_started = True
         _return_results.client_ok = False
         #WARNING ! shell=False is a safety measure to minimize XSS injections, don't change unless you know what the implications are
         self.process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
         
         #wait         
         self.process.wait() 
         
         #todo: needs pushing on a queue to handle threads
                          
         stdout, stderr = self.process.communicate()

         #todo : capture kill sig
               
         #pass stderr
         for _error, _tag in autonomi_messages._error_messages.items(): 
            if _error.lower() in stderr.lower(): 
               _stderr_break = True
               if _tag.lower() == autonomi_messages._error_network.lower():
                  _return_results.network_error = True
               elif _tag.lower() == autonomi_messages._error_client.lower():
                  _return_results.client_error = True
               elif _tag.lower() == autonomi_messages._error_dataloss.lower():
                  _return_results.network_data_loss = True
         
               log_writer.log(f"ant_client.quote: processing stderr found a match | _return_tag={_tag}",logging.DEBUG)
            #endIf

            #check if error has been found, and break
            if _stderr_break:
               break
         #endFor

         if stdout:
            keyword = "total cost:"
            start = stdout.lower().find(keyword.lower())
            if start != -1:
               start += len(keyword)
               total_cost = stdout[start:].strip()
            #endIf

            if total_cost:
               log_writer.log(f"Got a quote of {total_cost}",logging.DEBUG)
               _return_results.cost=total_cost
            else:
               _return_results.client_error = True
         else:
            _return_results.client_error = True
         #endIf


      except subprocess.TimeoutExpired as e:
         _return_results.client_error = True
         _stderr_break = True
         log_writer.log(f"ant_client.quote: client process was timed out",logging.DEBUG)
      except subprocess.CalledProcessError as e:
         _return_results.unknown_error = True
         _stderr_break = True
         log_writer.log(f"ant_client.quote: Unknown exception occured in client process",logging.DEBUG)
      except FileNotFoundError:  #to-do : should be using common dictionary
         cls_agent.Exception.throw(error=(f"{self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: File Not Found"))
         _stderr_break = True
         _return_results.client_error = True
         self._stop_watchdog.set()
         return "Error: not_found" # don't change the wording as we look for a match in other modules
      finally:
         if not _stderr_break:
            log_writer.log(f"ant_client.quote: client process exit clean",logging.DEBUG)
            _return_results.client_ok = True
      #endTry

       #todo : need to strip and return cost
      self._stop_watchdog.set()

      return _return_results

   def download(self, file_address : typedef_Agent_Client_File, timeout : int) -> typedef_Agent_Client_Response:
      
      self.__start_watchdog()

      _return_results : typedef_Agent_Client_Response = typedef_Agent_Client_Response()
      _stderr_break = False

      # BOILER: todo
      log_writer.log(f"ant_client:download: Start | file: {file_address.name} | address: {file_address.address}",logging.DEBUG)        

      temp_file_name = self.__get_temp_filepath(file_address.name)
      temp_file_name_log = cls_agent.Configuration.CLIENT_LOGGING_PATH

      #pass custom peers from environment
      if cls_agent.Configuration.CLIENT_PEERS:
         command = [ 
            './bin/ant', 
            '--peer', str(cls_agent.Configuration.CLIENT_PEERS),
            '--timeout', str(timeout),
            '--ignore-cache',
            '--log-output-dest', 
            temp_file_name_log, 
            'file', 
            'download', 
            file_address.address, 
            temp_file_name 
         ]
      else:
         command = [ 
            './bin/ant', 
            '--timeout', str(timeout), 
            '--ignore-cache',
            '--log-output-dest', 
            temp_file_name_log, 
            'file', 
            'download', 
            file_address.address, 
            temp_file_name 
         ]
      #endIf
      
      try:
         #needs wrapping in a timer

         _return_results.client_started = True
         _return_results.client_ok = False
         #WARNING ! shell=False is a safety measure to minimize XSS injections, don't change unless you know what the implications are
         self.process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
         
         #wait         
         self.process.wait() 
         
         #todo: needs pushing on a queue to handle threads
                          
         stdout, stderr = self.process.communicate()

         #todo : capture kill sig
         
         #pass stderr
         for _error, _tag in autonomi_messages._error_messages.items(): 
            if _error.lower() in stderr.lower(): 
               _stderr_break = True
               if _tag.lower() == autonomi_messages._error_network.lower():
                  _return_results.network_error = True
               elif _tag.lower() == autonomi_messages._error_client.lower():
                  _return_results.client_error = True
               elif _tag.lower() == autonomi_messages._error_dataloss.lower():
                  _return_results.network_data_loss = True
         
               log_writer.log(f"ant_client.download: processing stderr found a match | _return_tag={_tag}",logging.DEBUG)
            #endIf

            #check if error has been found, and break
            if _stderr_break:
               break
         #endFor

      except subprocess.TimeoutExpired as e:
         _return_results.client_error = True
         _stderr_break = True
         log_writer.log(f"ant_client.download: client process was timed out",logging.DEBUG)
      except subprocess.CalledProcessError as e:
         _return_results.unknown_error = True
         _stderr_break = True
         log_writer.log(f"ant_client.download: Unknown exception occured in client process",logging.DEBUG)
      except FileNotFoundError:  #to-do : should be using common dictionary
         cls_agent.Exception.throw(error=(f"{self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: File Not Found"))
         _stderr_break = True
         _return_results.client_error = True
         self._stop_watchdog.set()
         return "Error: not_found" # don't change the wording as we look for a match in other modules
      finally:
         if not _stderr_break:
            log_writer.log(f"ant_client.download: client process exit clean",logging.DEBUG)
            _return_results.client_ok = True
      #endTry

      #todo: process md5 - and check the file downloaded first - if file exists else we error, and waste time 
      if file_address.md5 and _return_results.client_ok:
         _return_results.md5_checked = True
         
         file_md5 = self.verify_md5(self.__get_single_filename(temp_file_name),file_address.md5)
         if file_md5:
            _return_results.md5_valid = True

      #endIf

      #todo : not the right place for this, it doesn't handle exception cleanup
      try:
         self.__del_temp_filepath(filepath=temp_file_name)
      except Exception as e:
         #todo : need to know why this is throwing an error, as it has it's own try catch in def :/
         pass

      self._stop_watchdog.set()

      return _return_results

##to-do : new hashed this is low   
   def calculate_md5(self,file_path): 
      hasher = hashlib.md5() 

      try:
         with open(file_path, 'rb') as file: 
            while chunk := file.read(8192): 
               hasher.update(chunk) 
      except Exception as e:
         return None
      return hasher.hexdigest() 
   
   def verify_md5(self,file_path, supplied_hash): 
      file_md5 = self.calculate_md5(file_path) 
      return file_md5 == supplied_hash
   
   def upload(self, filename, timeout=30):
      # BOILER: todo
      self.__start_watchdog()
      pass

   def version(self):
      try:
         result = subprocess.run(['./bin/ant', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
         return result.stdout.strip()
      except subprocess.CalledProcessError as e:
         return f"Error: {e.stderr.strip()}"
      except FileNotFoundError:
         cls_agent.Exception.throw(error=(f"{self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: File Not Found"))
         return "Error: not_found" # don't change the wording as we look for a match in other modules
