Current Status : The code is **pre-alpha** and full of place-holders and boiler plate code, however it should compile and execute in a fashion.

Notice : Please don't run this unattended, it's not stable enough currently.

The TODO.md will be kept upto date(tm) with areas that need attention.

## Distributed Agent Tests

The agent looks at this Github Repo for task scripts, they are found under **test-files**, the main control file that tells the agent what to do is '00-control.xml'

So why a centralised control script ?

The issue with testing agents, is they can be **too agressive** in their actions, and this "could" be detrimental to the network, and the aim of this is not to be a Distributed DDOS network.

Why can't the Agent run 1000's of test on my machine I have 132 Cores, and 1TB of memory ?

As above, the Agent has in-built rate limiters, set at an optimal level - they will ensure that if a "centralised" test asks the agent to run 5000 parallel downloads, it will ignore it, and default to a much lower "safe" level.

I think the agent tests are causing issues on the network ?

That's not a probelm, **ANYONE** can stop all the agents, by creating a Github issue in this repo, and using the tag "kill-switch", with some details around what they were seeing and why.  As soon as that issue is created, Agents will notice, and start killing worker threads until they are running no tests (This isn't instant, and can take upto 60 minutes).

Why are tests only scheduler and executed in a 50 minute hourly window ?

Good question :) As the agents are distributed, it is very hard with TimeZones to be confident that tests are all running when they are meant to.  The solution to that is, the Agent only runs tests from 5 minutes past the hour, till around 55 minutes to the hour, in Hourly cycles.

Outside that window, the Agent actively encourages running tasks to terminate, before forceably killing any straglers by 00 minutes.

## What can the Agent do ?

The agent runs a **Performance** worker, which collates run-time figures (how long a task took, did it suceed, was the file ok, what errors were seen) and then pushes the information to disk once a minute via a cache (to save on disk I/O) in
an InfluxDB line protocol specification.

Currently the agent has (3) modes of operation:

* Download - In this mode, the agent will download files from the network, either **once**, or multiple times in Hourly test window, multipled by the number of workers.  It can also check an MD5 hash of the file to ensure no corruption.
* Quote - In this mode, the agent retrieves specification of random seeds (which would allow the file to be regenerated for testing) it can use to generate files, from which it will request **quotes** from the network.
* Upload - In this mode, the agent will retrieve file specifications based on random seeds again, it will the upload to the network.

### What if I want more tests ?

The agent is coded to use threads, which allow it to do multiple **tests** at the same time - it is possible the agent could be tasked with parallel jobs to be downloading files of various sizes, while getting quotes, and uploading at the same time - this is why the **Rate-Limiter* is in the code, to ensure an Agent isn't bombareded with too much (machine spec also plays a role in the ability of the Agent)

## Building from source

The agent is written in pyton and requires a minimum version of **3.10**

1) you will need to make a clone for this repo, from either the **main** branch - bleading edge, or from one of the **released** branches - check out the CHANGELOG.md to see what's new.

```
git clone https://github.com/safenetforum-community/ant-agent/

cd ant-agent

git checkout main
```

2) install the python required modules, this is made easier by having a **requirements.txt** with the definitions in
```
pip install -r requirements.txt
```

### Autonomi binary requirements

The agent runs a wrapper around the autonomi supplied binaries, and as such - you will need to download them specifically to run with the agent.  It doesn't matter if you use *antup* or have put the binaries you currently have in your system path.  The agent specifically makes use of it's own copy of the binary.

1) you will need to download the complete binary distribution for linux, from the autonomi github - it usually contains all the files.

```wget .....```

2) the agent expects the autonomi client binary to be **executable** in a /bin directory under ant_agent

```
mkdir bin
unzip *.zip bin
cd bin
chmod +x autonomi
```

## Running the Agent

Currently the agent needs an open console / ssh connection - it currently won't behave very well being hupped, muxed, or screened.

The AGENT does **NOT** need root access, or sudo, please only execute as a normal low privelage user.

system requirements:

* min 10GB free hdd
* 1 core
* 512MB memory free

The agent can be launched from the ant_agent directory with.

```python3 ./src/main.py```

you should get the startup logs (currently in DEBUG)

```
16-12-2024 07:22:25 - INFO - Name: ant-agent | Version: 0.1.1 | Date: 14-12-2024 | Commit Hash: 410f9ce5b5fb18ded384e30f68e60283dec880e3
16-12-2024 07:22:25 - INFO - Found client: autonomi-cli 0.1.5
16-12-2024 07:22:25 - DEBUG - ScheduleManager.__run_watchdog: Watchdog thread started
16-12-2024 07:22:25 - INFO - Starting Agent task refresh schedule (TM) to check github for jobs at :00
16-12-2024 07:22:25 - INFO - Fetching tasks and jobs from github XML and updating schedule
16-12-2024 07:22:25 - DEBUG - ScheduleManager.pause_schedule : Finished
16-12-2024 07:22:25 - DEBUG - ScheduleManager.clear_schedule : Finished
+--------+--------+----------+----------+----------+----------+---------------------------------------------------------------------------+
|   Task |   Mins |   Worker | Repeat   |   Offset | Type     | Description                                                               |
+========+========+==========+==========+==========+==========+===========================================================================+
| 001    | 5      | 5        | false    | 0        | Download | Download a tiny file from network once an hour at 5 minutes past the hour |
+--------+--------+----------+----------+----------+----------+---------------------------------------------------------------------------+
16-12-2024 07:22:25 - DEBUG - ScheduleManager.resume_schedule : Finished
16-12-2024 07:22:25 - INFO - Rate Limiting Active : Download (360 calls in 3600 sec) | Upload (120 calls in 3600 sec) | Quote (240 calls in 3600 sec)
16-12-2024 07:22:25 - INFO - Press [q] = terminate agent | [f] = fetch updated tasks | [s] = show current status -> all keypress have a (10 second delay)

```

## Metrics

The agent is designed to generate InfluxDB line protocol files, and these will be stored in the **/cache/metrics/** directory under the agent.

There are currently two files;

``metrics.csv``  This is a per worker thread detailed performance stats  

``summary.csv``  This is a 1 minute rollup summary

### InfluxDB local

There is a **docker-compose.yml** under InfluxDB, that will start a local influx database, you will need to create ENV files with the docker file, to specify username, password, and token to login.

You can then access the influxDB interface on ``http://localhost:8086``

You can then import the Metrics manually into InfluxDB and visulise the data
