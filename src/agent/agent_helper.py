"""
===================================================================================================
Title : agent_helper.py

Description : helper utilities that don't fit in other classes

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import datetime
import random
from application import Agent

cls_agent = Agent()

class Utils:
    def scheduler_no_tasks_window(self): 
        current_minute = datetime.datetime.now().minute 
        if current_minute in cls_agent.Configuration.SCHEDULER_NO_TASKS:  
            return True 
       #endIf

    # Generate random minute between 0 and offset_minutes
    def offset(offset_minutes):
        if int(offset_minutes) < 0:
            return 0
        elif int(offset_minutes) > cls_agent.Configuration.DOWNLOAD_OFFSET_MAX_MINS:
            offset_minutes=cls_agent.Configuration.DOWNLOAD_OFFSET_MAX_MINS
        #endIfElse

        #add a delta to the offset
        random_multiplier = random.randint(30, 60) 
        offset_seconds = random.randint(1, int(offset_minutes)) * random_multiplier # if it's zero we error, and we handle zero further up

        return (offset_seconds)

