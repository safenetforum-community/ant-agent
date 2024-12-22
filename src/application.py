"""
===================================================================================================
Title : application.py

Description : Instance of the agent, with all application specific classes

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

class Agent:
    #Ensure this is a single instance class
    _instance = None

    #Thread Control Signals
    __bool_agent_terminate = False               # Set to True when agent is being shutdown
    __bool_threads_terminate = False    
    __bool_threads_scheduler_paused = False

    __int_thread_task_count = 0
    __int_thread_worker_count = 0
    
    import version              # Version Information on Agent
    import type_def             # Custom Data Types

    Exception = None            # Application Exception Handler class
    Configuration = None        # Application Configuration
   
# +++ Start: Single Instance class init
    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(Agent, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True

    def start(self):       #must be called once to initilize the instances, but can't be called in __init__ as circular
        if not hasattr(self, 'started'):
            # Esure start runs only once
            self.started = True
            
            if not self.Exception:
                self.Exception = _Agent__ExceptionHandler()

            if not self.Configuration:
                self.Configuration = _Agent__Configuration()
# +++ Definitions

    #Thread Task
    def push_thread_task(self):
        self.__int_thread_task_count+=1
    def pop_thread_task(self):
        self.__int_thread_task_count-=1
    def get_thread_task(self) -> int:
        return self.__int_thread_task_count
    
    #Thread Worker
    def push_thread_worker(self):
        self.__int_thread_worker_count+=1
    def pop_thread_worker(self):
        self.__int_thread_worker_count-=1
    def get_thread_worker(self) -> int:
        return self.__int_thread_worker_count


    def is_Threads_Terminate_Requested(self) -> bool:
        return self.__bool_threads_terminate
    def set_Threads_Terminate(self):
            self.__bool_threads_terminate = True
    def clear_Threads_Terminate(self):
            self.__bool_threads_terminate = False


    def is_Scheduler_Paused(self) -> bool:
        return self.__bool_threads_scheduler_paused
    def start_Scheduler(self):
        self.__bool_threads_scheduler_paused = False
    def pause_Scheduler(self):
        self.__bool_threads_scheduler_paused = True
    
    def __set_agent_shutdown(self):
        self.__bool_agent_terminate = True
        self.set_Threads_Terminate()

    def is_Agent_Shutdown(self) -> bool :
        return(self.__bool_agent_terminate)
    def exec_Shutdown(self):
        self.__set_agent_shutdown()
        #will need a handler to give threads time
       

# Global handler to allow threads a method of calling back to the main.py routine, to flag they have
# experienced an exception - Fatal, that should cause the program to terminate.
#
# Notes : This is a single instance class, so ensure that is enforced.
class _Agent__ExceptionHandler:
    #Ensure this is a single instance class
    _instance = None

    _class_exception = False
    _class_exception_err = None
    
    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(_Agent__ExceptionHandler, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True 

    # Check if a program exception has been raised
    def has_occurred(self):
        if self._class_exception:
            return True
        else:
            return False
        #endIf

    def get(self):
        return (self._class_exception_err)
    
    # can use following shorthand, to extract calling class, by importing inspect module
    # {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}
    def throw(self, error=None):
        self._class_exception_err = ""
        if error is not None: 
            if isinstance(error, str): 
                self._class_exception_err = error 
            #endIf
        #endIf
        self._class_exception=True


# Notes : This is a single instance class, so ensure that is enforced.
class _Agent__Configuration:
    #Ensure this is a single instance class
    _instance = None
    
    from telemetry import Telemetry                 # import telemetry defaults
    _Telemetry = None

    # European date format
    DATE_FORMAT = '%d-%m-%Y %H:%M:%S'

    # Logging constants
    LOG_FILE_PATH = './agent-ant.log'
    LOG_TO_FILE = False
    DEFAULT_LOG_LEVEL = 'INFO'  # DEBUG, ERROR, WARN, INFO #to-do : needs changing else too verbose

    SCHEDULER_CHECK = ":00" # What time (minutes) the scheduler will check for new jobs
    SCHEDULER_URL = 'https://raw.githubusercontent.com/safenetforum-community/ant-agent/main/tests/00-control.xml'
    SCHEDULER_NO_TASKS = [56, 57, 58, 59, 0, 1, 2, 3, 4]   # minutes when the schedule can't start new tasks

    GIT_OWNER = "safenetforum-community"
    GIT_REPO = "ant-agent"
    GIT_KILL_SWITCH_URL = "https://api.github.com/repos/{owner}/{repo}/issues"

    CACHE_FILE = './cache/cached_files.csv' 
    CACHE_INFO_FILE = './cache/cache_info.json' 
    CACHE_TIME = 3600 # 1 hour in seconds (must be only seconds)
    CSV_URL = 'https://raw.githubusercontent.com/safenetforum-community/ant-agent/main/tests/01-download-files.csv' 

    DOWNLOAD_YIELD_SECS = 10 # When in repeat mode, this is how many seconds we yield on a thread before repeating
    DOWNLOAD_OFFSET_MAX_MINS = 10 # Maximum minutes allows for offsetting tasks
    

    TELEMETRY_COUNTRY = None
    TELEMETRY_PROVISON = None
    TELEMETRY_CONNECTION = None

    CLIENT_MAX_OFFSET = 5                                # maximum minutes to be allowed in offset
    CLIENT_PEERS = None                                  # Peers used to bootstrap the client
    CLIENT_DOWNLOAD_PATH = "./cache/downloads"           # temporary location of downloaded files
    CLIENT_LOGGING_PATH = "./cache/log/"                 # Temporary location for client logging

    AGENT_LOCALE = "en_US"              # default locals

    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(_Agent__Configuration, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True 

            self._Telemetry = self.Telemetry()

    def load (self):
        #todo - load settings from env, config file, and pass any args
        global DEFAULT_LOG_LEVEL
        global LOG_TO_FILE
        
        DEFAULT_LOG_LEVEL = 'DEBUG'
        LOG_TO_FILE = True

        global TELEMETRY_COUNTRY
        TELEMETRY_COUNTRY = self._Telemetry.get()["country"]

        global TELEMETRY_PROVISON
        TELEMETRY_PROVISON = self._Telemetry.get()["provision"]

        global TELEMETRY_CONNECTION
        TELEMETRY_CONNECTION = self._Telemetry.get()["connection"]

        self._loadenv() # Load environment variables

    def _loadenv(self):
        import os
        from dotenv import load_dotenv

        # Load environment variables from a specific .env file
        load_dotenv(dotenv_path='./.env')
        for attribute in dir(self):
            if not attribute.startswith("_") and attribute.isupper():
                env_value = os.getenv(attribute)
                if env_value is not None:
                    current_value = getattr(self, attribute)
                    if isinstance(current_value, list):
                        # Convert env value back to list
                        setattr(self, attribute, list(map(int, env_value.split(','))))
                    elif isinstance(current_value, int):
                        setattr(self, attribute, int(env_value))
                    elif isinstance(current_value, float):
                        setattr(self, attribute, float(env_value))
                    else:
                        setattr(self, attribute, env_value)
