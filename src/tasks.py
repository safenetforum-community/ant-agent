"""
===============================================================================
Title : tasks.py

Description : Task loader and task definition

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import xml.etree.ElementTree as ET
import requests
import logging
from log import LogWriter
from application import Agent

# handle to logging
log_writer = LogWriter()
cls_agent = Agent()

class Agent_Task:
    def __init__(self, task_ref, description, time_period, time_offset, test_type, test_options):
        self.task_ref = task_ref
        self.description = description
        self.time_period = time_period
        self.time_offset = time_offset
        self.test_type = test_type
        self.test_options = test_options

    def __repr__(self):
        return (f"Task(task_ref={self.task_ref}, description={self.description}, "
                f"time_period={self.time_period}, time_offset={self.time_offset}, "
                f"test_type={self.test_type}, test_options={self.test_options})")

    #todo: need better exception handling to deal with badly formed XML
    def fetch_and_parse_xml(url):
        try:
            response = requests.get(cls_agent.Configuration.SCHEDULER_URL)
            response.raise_for_status()  # Raise an exception if the request fails
        except requests.exceptions.RequestException as e:
            log_writer.log(f"Error fetching the XML data: {e}", logging.ERROR)
            cls_agent.Exception.throw(error=f"tasks.fetch_and_parse_xml: Error {e}")
            return []
        #endTry

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            log_writer.log(f"Error parsing the XML data: {e}", logging.ERROR)
            cls_agent.Exception.throw(error=f"tasks.fetch_and_parse_xml: Error {e}")
            return []
        #endTry

        tasks = []

        #need better validation processing here
        for task in root.findall('Task'):
            try:
                task_ref = task.find('TaskRef').text
                description = task.find('Description').text[:100]
                time_period = task.find('TimePeriod').text
                time_offset = task.find('TimeOffset').text
                test_type = task.find('TestType').text

                test_options = {}
                for option in task.find('TestOptions').findall('Option'):
                    test_options[option.attrib['key']] = option.attrib['value']
                #endFor

                tasks.append(Agent_Task(task_ref, description, time_period, time_offset, test_type, test_options))
            except AttributeError as e:
                #todo: better handling needed here
                log_writer.log(f"Error processing a task element: {e}",logging.ERROR)
            #endTry
        #endFor
        
        return tasks
