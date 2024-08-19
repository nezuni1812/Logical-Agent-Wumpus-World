# Logical-Agent-Wumpus-World
Introduction to Artificial Intelligence (HCMUS) - Project 2: Logical Agent

This repository contains our code for the group homework of the class Introduction to Artificial Intelligence.

The inputs, classes definition and main UI code are included in this repository.

Source code:  [GitHub](https://github.com/nezuni1812/Logical-Agent-Wumpus-World)

# Demo video:
[![Video](https://img.youtube.com/vi/4KwkVteSj-M/maxresdefault.jpg)](https://youtu.be/4KwkVteSj-M)

# Running the UI:
All of our code are written in Python so a system with a relatively modern version of Python (>= 3.10) and PIP are required to run the program.

## Installing dependencies
```bash
pip install -r requirements.txt
```
## Running the UI
The working director MUST be the one contains all input files, font file and image folder.
```bash
cd Source
```
So our working directory will have:
```
Source (we are in here)
│   main.py
│   CascadiaCode.ttf
│   map1.txt
│   ...
│   map6.txt
│   result1.txt
│   ...
│   result6.txt
│   README.txt
│   Interface.py
│   Agent.py
│   Program.py
│   KnowledgeBase.py
│   requirements.txt
│   ...
│   
└───resource
        agent.png
        ...
```
Then we run the program with Python.
```bash
python main.py
```

# Changing map inputs
There are several input files to choose from. Their names are:

`map1.txt`\
`map2.txt`\
...\
`map8.txt`\

User can directly edit the input file name in the `main.py` file by commenting and uncommenting which file the `Program` should take.
