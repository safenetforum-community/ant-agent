Current Status : The code is **pre-alpha** and full of place-holders and boiler plate code, however it should compile and execute in a fashion.

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
