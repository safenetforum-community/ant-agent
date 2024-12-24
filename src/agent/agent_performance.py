"""
===================================================================================================
Title : agent_performance.py

Description : logging and processing of performance stats

Copyright 2024 - Jadkins-Me

This Code/Software is licensed to you under GNU AFFERO GENERAL PUBLIC LICENSE (GPL), Version 3
Unless required by applicable law or agreed to in writing, the Code/Software distributed
under the GPL Licence is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. Please review the Licences for the specific language governing
permissions and limitations relating to use of the Code/Software.

===================================================================================================
"""

# reference from other objects with
# from performance import Performance 
# perf = Performance()

import time
import os
import threading
import logging
import datetime
import inspect
from log import LogWriter
from collections import defaultdict
from typing import Optional
from application import Agent
from type_def import typedef_Agent_Performance

cls_agent = Agent()
log_writer = LogWriter()

class Performance:
    #Ensure this is a single instance class
    _instance = None
    #to-do: this is a mess, need to rationalize
    mem_metrics = []
    metrics_file = "./cache/metrics/metrics.csv"
    metrics_summary_file = "./cache/metrics/summary.csv"
    perf_influxdb = "_ant_agent"
    perf_influxdb_summary = "".join([perf_influxdb, "_smry"])
    
    def __new__(cls, *args, **kwargs): 
        if not cls._instance: cls._instance = super(Performance, cls).__new__(cls, *args, **kwargs) 
        return cls._instance 
    
    def __init__(self): 
        if not hasattr(self, 'initialized'): 
            # Ensure __init__ runs only once 
            self.initialized = True 
            # Initialize stuff here !! TO-DO # this is a mess
            self.except_handler = Exception()
            try:
                os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True) 
                os.makedirs(os.path.dirname(self.metrics_summary_file), exist_ok=True) 
            except Exception as e:
                cls_agent.Exception.throw(error=(f"{self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: Permission or File access Error"))
            
            self.flush_thread = threading.Thread(target=self.__flush_periodically, daemon=True, name="Thread-4(Performance._flush_periodically)") 
            self.flush_thread.start()       

    def __flush_periodically(self): 
        # Background thread method to flush metrics every 1 minute 
        while True: 
            time.sleep(60) 
            self.__1_min_flush()     
            #to-do need to handle thread termination, as it might hang exit in waiting state

    def __flush_mem_metrics_to_disk(self):
        # Use a temporary list to store the current metrics

        _temp_metrics = self.mem_metrics[:] 
        self.mem_metrics = []

        #provide compiler hint
        _metric : typedef_Agent_Performance = []

        if len(_temp_metrics) > 0:
            with open(self.metrics_file, 'a') as file: 
                for _metric in _temp_metrics: 
                    file.write((
                        f"{self.perf_influxdb},"
                        f"tele_c={cls_agent.Configuration.TELEMETRY_COUNTRY},"
                        f"tele_p={cls_agent.Configuration.TELEMETRY_PROVISON},"
                        f"type=\"{_metric.test_type}\" "    #need a space here at end
                        f"filesize=\"{_metric.filesize}\","
                        f"md5checker={int(_metric.md5_checked)},"
                        f"md5valid={int(_metric.md5_valid)},"
                        f"cost={_metric.cost},"
                        f"client_ok={int(_metric.client_ok)},"
                        f"client_kill={int(_metric.client_killed)},"
                        f"client_err={int(_metric.client_error)},"
                        f"network_err={int(_metric.network_error)}," 
                        f"data_loss={int(_metric.network_data_loss)}," 
                        f"unknown_err={int(_metric.unknown_error)}," 
                        f"exec_time={_metric.execution} " #need a space here at end
                        f"{self.__get_influxdb_time()}\n"))
                #endFor
            #endWith
        #endIf
        
    def __1_min_flush(self): 
        # Every 1 minute, calculate stats and flush metrics to disk 
        self.__calculate_stats() 
        self.__flush_mem_metrics_to_disk()

    def shutdown(self): 
        # Shutdown the Performance instance 
        self.__flush_mem_metrics_to_disk() 
        self._instance = None

    def __get_influxdb_time(self):
        # Get current UTC time 
        current_time = datetime.datetime.utcnow() 
        
        # Get the time since Unix Epoch in nanoseconds 
        epoch_time_ns = int(time.mktime(current_time.timetuple())) * 1_000_000_000 + current_time.microsecond * 1_000 
        
        return epoch_time_ns
    
    def __calculate_stats(self):
        # Calculate statistics for all metrics in mem_metrics 
        stats = defaultdict(lambda: {'count': 0, 'min': float('inf'), 'max': float('-inf'), 'total_time': 0}) 

        #provide compiler hint
        _metric : typedef_Agent_Performance = []
        
        for _metric in self.mem_metrics: 
            name, time = _metric.test_type, _metric.execution 
            stats[name]['count'] += 1 
            stats[name]['min'] = min(stats[name]['min'], time) 
            stats[name]['max'] = max(stats[name]['max'], time) 
            stats[name]['total_time'] += time 
        
        with open(self.metrics_summary_file, 'a') as file: 
            for name, data in stats.items(): 
                mean_time = round( data['total_time'] / data['count'], 2) 
                file.write(f"{self.perf_influxdb_summary},type={name},min={data['min']},max={data['max']},mean={mean_time},count={data['count']} {self.__get_influxdb_time()}\n")

    def add_metric(self, results: typedef_Agent_Performance ):
        log_writer.log(f"+ + {self.__class__.__name__}/{inspect.currentframe().f_code.co_name}: Add Metric -> {results.test_type},{results.execution:.2f}s", logging.INFO) 
        self.mem_metrics.append(results)

class Test: 
        def __init__(self): 
            self._performance = Performance() # Get the singleton instance of Performance 

        def start_timer(self):
            self._start_time = time.time()

        def stop_timer(self):
            if self._start_time is not None: 
                self.execution_time = time.time() - self._start_time #native in seconds, might need over-ride to prevent any interpriter sillyness
                self._start_time = None   

        def add_results(self, results: typedef_Agent_Performance ):
            results.execution = round(self.execution_time, 2) #todo - limit to 2 decimals
            self._performance.add_metric(results) 
            del self
