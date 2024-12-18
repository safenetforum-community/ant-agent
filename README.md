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

