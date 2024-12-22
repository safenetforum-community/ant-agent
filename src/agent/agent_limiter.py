"""
===================================================================================================
Title : agent_limiter.py

Description : global limiter to manager total agent load

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""
from ratelimit import limits, RateLimitException 
from log import LogWriter 
import logging 
from datetime import datetime, timedelta
from application import Agent


# Notes : This is a single instance class, so ensure that is enforced.
class Limiter:
    #Ensure this is a single instance class
    _instance = None
    _last_exception_time = None

    #handle to log processing
    log_writer = LogWriter()
    cls_agent = Agent()

    LIMITER_DOWNLOAD_RATE_SECONDS = 3600        # 1 hour
    LIMITER_DOWNLOAD_RATE_COUNT = 360           # ~ 1 download per 10 seconds    

    LIMITER_UPLOAD_RATE_SECONDS = 3600          # 1 hour
    LIMITER_UPLOAD_RATE_COUNT = 120             # ~ 2 upload per 1 minute

    LIMITER_QUOTE_RATE_SECONDS = 3600           # 1 hour
    LIMITER_QUOTE_RATE_COUNT = 240              # ~ 4 quote per 1 minute  

    # Define the cooldown period for handling RateLimitException (5 minutes) 
    CONST_FIVE_MINUTES = timedelta(minutes=5) 

     #to-do - BROKEN, need to sort out the scope and debug
    def download_rate_limit(self,func): 
        def wrapper(*args, **kwargs): 
            try: 
                return func(*args, **kwargs) 
            except RateLimitException: 
                current_time = datetime.now() 
                if current_time - self._last_exception_time >= self.CONST_FIVE_MINUTES: 
                    self._last_exception_time = current_time 
                    self.log_writer.log(f"!!! Download: Agent Rate limit applied | too many download requests, suppressing logging for 5 minutes", logging.INFO) 
                return False, None 
        return wrapper

    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(Limiter, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True
            
            # Timestamp to track the last time the rate limit exception was handled 
            self._last_exception_time = datetime.min

            #todo: Apply the decorator dynamically - this needs re-work
            self.__download_limiter = self.download_rate_limit( self.__download_limiter)

    @limits(calls=LIMITER_DOWNLOAD_RATE_COUNT, period=LIMITER_DOWNLOAD_RATE_SECONDS) # Adjusted to 2 requests per hour 
    def __download_limiter(self): 
        return True , None

    def is_ratelimit_download(self) -> bool: 
        try: 
            result,_ = self.__download_limiter() 
            return not result
        except RateLimitException: 
            return True # Return True when limit is reached

    def is_ratelimit_upload(self) -> bool:
        return False

    def is_ratelimit_quote(self) -> bool:
        return False
    
    def show_limits(self):
        #to:do
        self.log_writer.log(f"Rate Limiting Active : Download ({self.LIMITER_DOWNLOAD_RATE_COUNT} calls in {self.LIMITER_DOWNLOAD_RATE_SECONDS} sec) | Upload ({self.LIMITER_UPLOAD_RATE_COUNT} calls in {self.LIMITER_UPLOAD_RATE_SECONDS} sec) | Quote ({self.LIMITER_QUOTE_RATE_COUNT} calls in {self.LIMITER_QUOTE_RATE_SECONDS} sec)",logging.INFO)
        