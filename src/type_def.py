"""
===================================================================================================
Title : type_def.py

Description : Type Definitions that can be shared by classes

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

from dataclasses import dataclass
from typing import Literal

# Define the literals 
_TestType = Literal['download', 'upload', 'quote']
_filesize = Literal['tiny','small','medium','large','huge','giga','tera']

# used in /client/ modules to return response codes
@dataclass
class typedef_Agent_Client_Response: 
    md5_checked : bool = False           # True, md5 hash was checked
    md5_valid   : bool = False           # True, the md5 of the file matches the provided hash
    client_started : bool = False        # True, the wrapped binary was launched
    client_ok      : bool = False        # True, the client ran as expected
    client_killed : bool = False         # True, the client process had to be killed due to hanging, or long running process
    client_error : bool = False          # True, an error occured with the client
    network_error : bool = False         # True, an error occured with the network
    network_data_loss : bool = False     # True, a data loss event has occured
    unknown_error : bool = False         # True, an unknown error occured
#endClass 

@dataclass
class typedef_Agent_Task:
    task_ref : str = None                # Task Reference 000 through to 999
    time_period : str = None             # Time Period from 00 through to 59 (minutes)
    test_type : _TestType = None          # Type of test i.e. download, quote, upload
    description : str = None             # Brief description of task
    test_options : 'typedef_Agent_Task_Options' = None  # A class of class options
#endClass

@dataclass
class typedef_Agent_Task_Options:
    filesize : _filesize = None          # Task Filesize, small, tiny, medium etc
    workers : int = 1                    # Number of task workers to spawn
    offset : int = 0                     # Offset of task in minutes
    repeat : bool = False                # If True, then repeat the task
    retry : int = 0                      # retry count on failure
    timeout : int = 30                   # timeout for executing a command
#endClass

@dataclass 
class typedef_Agent_Client_File:
    address: str = ""                    # Client Xor Address
    name: str = ""                       # name of file without path
    md5: str = ""                        # md5 hash of file

@dataclass
class typedef_Agent_Performance:
    test_type: _TestType = None          # Type of Test
    filesize: _filesize = None           # File size
    execution: float = 0                 # How long the test took 
    md5_checked : bool = False           # True, md5 hash was checked
    md5_valid   : bool = False           # True, the md5 of the file matches the provided hash
    cost: float = 0            
    client_ok      : bool = False        # True, the client ran as expected
    client_killed : bool = False         # True, the client process had to be killed due to hanging, or long running process
    client_error : bool = False          # True, an error occured with the client
    network_error : bool = False         # True, an error occured with the network
    network_data_loss : bool = False     # True, a data loss event has occured
    unknown_error : bool = False         # True, an unknown error occured

@dataclass
class typedef_Agent_Downloader:
    filesize: _filesize = None
    offset : int = 0                     # Offset of task in minutes
    repeat : bool = False                # If True, then repeat the task, 
    timeout : int = 30                   # timeout for executing a command
    retry : int = 0                      # retry count on failure