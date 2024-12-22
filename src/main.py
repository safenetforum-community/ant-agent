"""
===================================================================================================
Title : main.py

Description : Entry point for the agent

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

# IMPORTS --------------------------------------------------------------------

from application import Agent
import logging
from log import LogWriter
import sys
import threading 
import queue 
import tty 
import termios 
import time
import select
from agent.agent_performance import Performance
from agent.agent_limiter import Limiter
from scheduler import ScheduleManager
from client.autonomi import ant_client

# DEFINITIONS ------------------------------------------------------------------
def getch(): 
    fd = sys.stdin.fileno() 
    old_settings = termios.tcgetattr(fd) 
    try: 
        tty.setraw(fd) 
        ch = sys.stdin.read(1) 
    finally: 
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings) 
        return ch
     
def pause_input_getch():
    global _getch_input_enabled
    _getch_input_enabled = False

def start_input_getch():
    global _getch_input_enabled
    _getch_input_enabled = True

def read_input(): 
    while True: 
        if _getch_input_enabled:
            ch = getch() 
            input_queue.put(ch) 
            if ch == 'q': 
                break

def flush_input(): 
    while select.select([sys.stdin], [], [], 0)[0]: 
        sys.stdin.read(1)

# MAIN -------------------------------------------------------------------------
if __name__ == "__main__":
    
    #application class single instance
    cls_agent = Agent()
    cls_agent.start()
    cls_agent.Configuration.load()
    
    #singleton class logging thread
    log_writer = LogWriter()
    log_writer.config()

    #handler for the main input loop
    input_queue = queue.Queue()
    _getch_input_enabled = False
    
    #Build Information
    log_writer.log(f"Name: {cls_agent.version.BUILD_NAME} | Version: {cls_agent.version.BUILD_VERSION} | Date: {cls_agent.version.BUILD_DATE} | Commit Hash: {cls_agent.version.COMMIT_HASH}", logging.INFO)
    
    #Detect if client can be found, else terminate
    client = ant_client()
    ant_version = client.version()
    if "not_found" in ant_version:
       log_writer.log(f"The autonomi 'ant' client command was not found. Have you installed it ?", logging.FATAL )
       sys.exit(1)
    else:
        log_writer.log(f"Found client: {ant_version}", logging.INFO)
    #endIfElse
   
    #Create an instance of global test schedule, which will chain all the worker threads
    schedule_manager = ScheduleManager()
    schedule_manager.fetch_tasks() #todo: should the agent load tasks, and start instantly or wait until next automatic refresh  

    #create performance logging and metric global instance
    perf = Performance()

    #rate limit handler for global requests
    rate_limit = Limiter()
    rate_limit.show_limits()

    #Show console update that we are running
    log_writer.log(F"Press [q] = Quit Agent | [f] = Fetch Tasks | [r] = Run task manually | [s] = show status -> all keypress have a (10 second delay)", logging.INFO)

     # Start the input reading thread 
    input_thread = threading.Thread(target=read_input, name="Thread-0(_main.read_input)") 
    input_thread.daemon = True 
    input_thread.start()
    start_input_getch()

    #Lazy main loop # todo - needs to support service / docker / webapp
    while True: 
        try: 
            user_input = input_queue.get_nowait() 
            if user_input == 'q':
                pause_input_getch()
                log_writer.log(f"Main.quit: Agent has received a stop signal.", logging.INFO)
                cls_agent.exec_Shutdown() 
                perf.shutdown()
                #to-do: capture threads, and report when done
                sys.exit(None)
                #end __main__
            elif user_input == 'f': 
                flush_input()
                pause_input_getch()
                schedule_manager.fetch_tasks()
                start_input_getch()
            elif user_input == 'r':
                flush_input()
                pause_input_getch()
                schedule_manager.run_task_manually()
                start_input_getch()
            #endIf
        except queue.Empty: 
            # handle this when no user input - should really be somewhere else
            if cls_agent.Exception.has_occurred():
                log_writer.log(f"Code exception has occured {cls_agent.Exception.get}",logging.FATAL)
                sys.exit(1)
                #end __main__ with FATAL exception
        # Sleep for 10 seconds 
        time.sleep(10)