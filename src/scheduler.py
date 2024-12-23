"""
===================================================================================================
Title : scheduler.py

Description : The schedule manager object, responsbile for spawning the tasks

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

import schedule
import inspect
import time
import threading
from application import Agent
import logging
from agent.agent_runner import AgentRunner
from tasks import Agent_Task
import kill_switch
from log import LogWriter
from agent.agent_helper import Utils
from tabulate import tabulate
from type_def import typedef_Agent_Task

#get a handle to logging class
log_writer = LogWriter()
cls_agent = Agent()

#get a handle to kill switch detection
killswitch_checker = kill_switch.GitHubRepoIssuesChecker()

#get a handle to helper utils
helper = Utils()

# Notes : This is a single instance class, so ensure that is enforced.
class ScheduleManager:
     #Ensure this is a single instance class
    _instance = None

    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(ScheduleManager, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True

            self.tasks = []         # holds the tasks we have spawned from the test plan, and enables them to be queried

            #Schedule Manager (SM) Schedule used for running jobs - can be paused, and cleared
            cls_agent.pause_Scheduler()
            self._stop_eventSM = threading.Event()
            self._schedulerSM = schedule.Scheduler()

            #Task Manager (TM) Schedule used solely for downloading jobs to run from github
            self._stop_eventTM = threading.Event()
            self._schedulerTM = schedule.Scheduler()

            self.scheduler_threadSM = threading.Thread(target=self.__run_pendingSM,name="Thread-1(Scheduler.ScheduleManager.SM)")
            self.scheduler_threadSM.start()
            cls_agent.start_Scheduler()

            self.scheduler_threadTM = threading.Thread(target=self.__run_pendingTM,name="Thread-1(Scheduler.ScheduleManager.TM)")
            self.scheduler_threadTM.start()

            self._stop_watchdog = threading.Event()
            self._watchdog = threading.Thread(target=self.__run_watchdog, name="Thread-1(Scheduler._watchdog)")
            self._watchdog.start()

            #to-do: change schedule to every minute for fast refresh, and ability to invoke refresh with rate limit
            self._schedulerTM.every().hour.at(cls_agent.Configuration.SCHEDULER_CHECK).do(self.fetch_tasks)
            #self._schedulerTM.every(1).minutes.do(self.fetch_tasks)
            log_writer.log(f"Starting Agent task refresh schedule (TM) to check github for jobs at {cls_agent.Configuration.SCHEDULER_CHECK}", logging.INFO)
        #endIf
    
    def __convert_to_colon_format(self, minutes_string):
        padded_minutes = f"{int(minutes_string):02d}"
        return f":{padded_minutes}"

    def __add_task(self, task):
        if self.task_already_scheduled(self.__convert_to_colon_format(task.time_period)):
            log_writer.log(f"Task already scheduled at {self.__convert_to_colon_format(task.time_period)}", logging.ERROR)
            return
        if task.test_type.lower() == "download":
            self._schedulerSM.every().hour.at(self.__convert_to_colon_format(task.time_period)).do(self.__downloadtask_schedule, task)
            self.tasks.append(task)
        elif task.test_type.lower() == "quote":
            self._schedulerSM.every().hour.at(self.__convert_to_colon_format(task.time_period)).do(self.__quotetask_schedule, task)
            self.tasks.append((task, "quote", self.__convert_to_colon_format(task.time_period)))
        elif task.test_type.lower() == "upload":
            self._schedulerSM.every().hour.at(self.__convert_to_colon_format(task.time_period)).do(self.__uploadtask_schedule, task)
            self.tasks.append((task, "upload", self.__convert_to_colon_format(task.time_period)))
        else:
            log_writer.log(f"Unknown test type: {task.test_type}", logging.ERROR)
            
    # Fetch_Tasks will query the source, and populate a TASKS object will all the tasks to execute
    def fetch_tasks(self):
        log_writer.log(f"Fetching tasks and jobs from github XML and updating schedule",logging.INFO)    
 
        #pause any existing schedules, and clear them
        self.pause_schedule()
        self.clear_schedule()
 
        #if killswitch is active, then we don't process any TASKS and we wait...      
        killswitch_found, datetime = killswitch_checker.check_for_kill_switch()
        if killswitch_found:
            log_writer.log(f"Kill-switch ON, test paused by github issue created {datetime}, agent active.",logging.WARNING)
        else:
            _tasks = Agent_Task.fetch_and_parse_xml(cls_agent.Configuration.SCHEDULER_URL)

            for task in _tasks:
                self.__add_task(task)

            self.list_schedules()

            self.__purge_envionment()

            self.resume_schedule()
        #EndIfElse

# ----> DOWNLOAD TASK SCHEDULER <--------------------------------------------------------------------------------------------------
    def __downloadtask_schedule(self, task):
        log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {task.task_ref}", logging.DEBUG )

        if helper.scheduler_no_tasks_window():
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: _scheduler_no_tasks_window: TRUE", logging.DEBUG )
            #We can't execute this schedule, as we are in a no-tasks window
        elif killswitch_checker.check_for_kill_switch()[0]:
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: check_for_kill_switch: TRUE", logging.DEBUG )
            #We can't execute this schedule, kill switch is active
        else:
            try:
                #pass the task over to the Agent Runner, we abaondon the thread, and allow its own watchdog to control it
                agent_runner = AgentRunner()
                #Note : args = tuple, so the random , is needed, else we don't pass the correct object
                _agent_thread = threading.Thread(target=agent_runner.exec_download_task,args=(task,),name=f"Thread-Runner.{task.task_ref}")
                _agent_thread.setDaemon(True) # Make the thread a daemon thread
                _agent_thread.start()

            except Exception as e:
                log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {e}", logging.ERROR)
            #endTry
        #endIfElse    
        
        log_writer.log(f"< < {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: return: NONE", logging.DEBUG )

# ----> QUOTE TASK SCHEDULER <--------------------------------------------------------------------------------------------------
    def __quotetask_schedule(self, task):
        log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {task.task_ref}", logging.DEBUG )

        if helper.scheduler_no_tasks_window():
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: _scheduler_no_tasks_window: TRUE", logging.DEBUG )
            #We can't execute this schedule, as we are in a no-tasks window
        elif killswitch_checker.check_for_kill_switch()[0]:
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: check_for_kill_switch: TRUE", logging.DEBUG )
            #We can't execute this schedule, kill switch is active
        else:
            try:
                #pass the task over to the Agent Runner to spawn the workers
                agent_runner = AgentRunner()
                #Note : args = tuple, so the random , is needed, else we don't pass the correct object
                _agent_thread = threading.Thread(target=agent_runner.exec_quote_task,args=(task,),name=f"Thread-Runner.{task.task_ref}")
                _agent_thread.setDaemon(True) # Make the thread a daemon thread
                _agent_thread.start()

            except Exception as e:
                log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {e}", logging.ERROR)
            #endTry
        #endIfElse    
        
        log_writer.log(f"< < {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: return: NONE", logging.DEBUG )

# ----> UPLOAD TASK SCHEDULER <--------------------------------------------------------------------------------------------------
    def __uploadtask_schedule(self, task):
        log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {task.task_ref}", logging.DEBUG )

        if helper.scheduler_no_tasks_window():
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: _scheduler_no_tasks_window: TRUE", logging.DEBUG )
            #We can't execute this schedule, as we are in a no-tasks window
        elif killswitch_checker.check_for_kill_switch()[0]:
            log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: check_for_kill_switch: TRUE", logging.DEBUG )
            #We can't execute this schedule, kill switch is active
        else:
            try:
                #pass the task over to the Agent Runner to spawn the workers
                agent_runner = AgentRunner()
                #Note : args = tuple, so the random , is needed, else we don't pass the correct object
                _agent_thread = threading.Thread(target=agent_runner.exec_upload_task,args=(task,),name=f"Thread-Runner.{task.task_ref}")
                _agent_thread.setDaemon(True) # Make the thread a daemon thread
                _agent_thread.start()
                
            except Exception as e:
                log_writer.log(f"> > {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: {e}", logging.ERROR)
            #endTry
        #endIfElse    
        
        log_writer.log(f"< < {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: return: NONE", logging.DEBUG )

# ----> LIST TASK <-----------------------------------------------------------------------------------------------------------
    def list_schedules(self):
        if not self.tasks:
            print("No tasks scheduled.")
        else:
            # Collect data for table, and store it in tabulate format 
            table_data = []

            for task in self.tasks:
                table_data.append( {
                    "Task": f"{task.task_ref}",
                    "Mins" : f"{task.time_period}",
                    "Worker": f"{task.test_options.get('workers', None)}", 
                    "Repeat": f"{task.test_options.get('repeat', False)}",
                    #"Offset": f"{task.test_options.get('offset', None)}",
                    "Type": f"{task.test_type}",
                    "Size": f"{task.test_options.get('filesize', None)}",
                    "Description": f"{task.description}" 
                }) 
            #EndFor

            # Create a nice looking table 
            table = tabulate(table_data, headers="keys", tablefmt="grid", numalign="centre")

            # todo - logger doesnt support tabulate format
            print(f"{table}")
        #endIfElse

    def get_status(self): #todo
        _table_data = []

        _main_thread = threading.main_thread() 
        _threads = threading.enumerate()
        _non_main_thread_names = [thread.name for thread in _threads if thread != _main_thread]

        _count_watchdog = 0
        _count_schedulemanager = 0
        _count_performance = 0
        _count_runner = 0
        for _thread in _non_main_thread_names:
            if "watchdog" in _thread.lower():
                _count_watchdog += 1
            elif "schedulemanager" in _thread.lower():
                _count_schedulemanager += 1
            elif "performance" in _thread.lower():
                _count_performance += 1
            elif "runner" in _thread.lower():
                _count_runner += 1
            #endIfElse    
        #endFor

        _table_data.append( {
            "Schedule Manager": f"{_count_schedulemanager}",
            "Thread Watchdog" : f"{_count_watchdog}",
            "Performance Writer": f"{_count_performance}", 
            "Task Runners": f"{_count_runner}"
        }) 

        # Create a nice looking table 
        table = tabulate(_table_data, headers="keys", tablefmt="grid", numalign="centre")

        print("\n" + table + "\n")

    #todo: needs optimisation
    def task_already_scheduled(self, time):
        #compiler hint
        _task : typedef_Agent_Task = typedef_Agent_Task()
        try:
            for _task in self.tasks:
                if _task.time_period == time:
                    return True
                #endIf
            #endFor
            return False
        except Exception as e:
            log_writer(f"ScheduleManager.task_already_scheduled: Threw Exception {e}", logging.DEBUG)
            return True #as something is wrong with the task time
        #endTry

    def run_task_manually(self):
        self.pause_schedule()
        self.list_schedules()
        log_writer.log(f"Please enter the Task Ref for the task to execute",logging.INFO)

        _response = input("Task Ref (blank to exit and resume schedule)=")

        #todo - needs finishing
        for task in self.tasks:
            if task.task_ref == _response:
                log_writer.log(f"Manually launching {_response}",logging.INFO)
                if task.test_type.lower() == 'download':
                    self.__downloadtask_schedule(task)
                elif task.test_type.lower() =='quote':
                    self.__quotetask_schedule(task)
                elif task.test_type.lower() =='upload':
                    self.__uploadtask_schedule(task)
                #endIfElse
            else:
                log_writer.log(f"Task Ref was not found...",logging.INFO)
            #endIf
        #endFor

        self.resume_schedule()

    def __run_pendingSM(self):
        while not self._stop_eventSM.is_set():
            if not cls_agent.is_Scheduler_Paused():
                self._schedulerSM.run_pending()
            time.sleep(1)

    def __run_pendingTM(self):
        while not self._stop_eventTM.is_set():
            self._schedulerTM.run_pending()
            time.sleep(1)

#watchdog, looking for global events to control threads in this class
    def __run_watchdog(self):
        log_writer.log(f"ScheduleManager.__run_watchdog: Watchdog thread started",logging.DEBUG)
        
        while not self._stop_watchdog.is_set():
            if cls_agent.is_Agent_Shutdown():
                self._stop_watchdog.set()
                self.terminate()
            if helper.scheduler_no_tasks_window() and not cls_agent.is_Threads_Terminate_Requested():
                cls_agent.set_Threads_Terminate()
            elif not helper.scheduler_no_tasks_window() and cls_agent.is_Threads_Terminate_Requested():
                cls_agent.clear_Threads_Terminate()
            #endIfElse

            time.sleep(1)
        #endWhile

        log_writer.log(f"ScheduleManager.__run_watchdog: Watchdog thread exited",logging.DEBUG)

    def __purge_envionment(self):
        #todo : routines to clear out old test runs, logs, and cache
        log_writer.log("ScheduleManager.__purge_environment: Purging previous temporary test files, this may take a few minutes",logging.INFO)

    def terminate(self):
        log_writer.log(f"ScheduleManager.Terminate: Started", logging.DEBUG)

        self._stop_eventSM.set()
        self._stop_eventTM.set()
        
        self.scheduler_threadSM.join()
        self.scheduler_threadTM.join()

        log_writer.log(f"ScheduleManager.Terminate: Finished", logging.DEBUG)

    def pause_schedule(self):
        cls_agent.pause_Scheduler()
        log_writer.log(f"ScheduleManager.pause_schedule : Finished", logging.DEBUG)

    def resume_schedule(self):
        cls_agent.start_Scheduler()
        log_writer.log(f"ScheduleManager.resume_schedule : Finished", logging.DEBUG)

    def clear_schedule(self):
        self._schedulerSM.clear()
        self.tasks = []
        log_writer.log(f"ScheduleManager.clear_schedule : Finished", logging.DEBUG)


