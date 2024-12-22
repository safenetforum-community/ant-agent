"""
===================================================================================================
Title : telemetry.py

Description : version module, easy to update from code

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

# This agent code does NOT automatically collect/process any telemetry information or metrics, about the user, client, or environment.
# Any telemetry data is defined by the user and is only collected if explicitly defined by the user.
# If no telemetry is specified by the user, a standard non-uniunique ignore pattern will be used.

# Notes : This is a single instance class, so ensure that is enforced.
class Telemetry:
     #Ensure this is a single instance class
    _instance = None

    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(Telemetry, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True

            #ignore pattern = xx
            self.__str_country_code = "xx"      # Country Code 2 digit 
            self.__str_agent_provision = "xx"   # Home / Cloud 
            self.__str_agent_connection = "xx"  # Connection type 
            
    #todo: needs some validation to make sure country code is only ever 2 digits, and dictionary is used for others so the options are defined
    def get(self): 
        return { 
            "country": self.__str_country_code, 
            "provision": self.__str_agent_provision, 
            "connection": self.__str_agent_connection 
            }