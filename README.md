runexp
======

Python script for running long/parallel simulations (either by direct execution or using oar). All command lines can be parametrized and loops can be programmed to execute the same command with multiple parameters.

## Features

- All jobs are configured in a unique file "jobs.ini" easy to understand. 
- Direct execution of given commands either can be performed in parallel or one after the other. 
- Builtin OAR (oarsub) execution format allows running of tasks on HPC clusters.

## Installation

- No particular installation required (a script runexp is provided).
- No particular python library outside of the STD lib.

## Short documentation


### Introduction

The command line help defines several options:
```bash
$./runexp
usage: runexp [-h] [-c CONFIGFILE] [-l] [-t] [-r] [-o] [-v] [-i] [-w]
              [task] [idx [idx ...]]

utility for launching parallel jobs (direct execution or oarsub)

positional arguments:
  task                  selected task
  idx                   subtask index(s) for selected execution

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configfile CONFIGFILE
                        config file (jobs.ini in current folder)
  -l, --list            show list of tasks
  -t, --test            test task launching (print commands)
  -r, --runonly         force direct run of command (without oarsub)
  -o, --oar             force the use of oarsub
  -v, --verbose         use verbose printing mode
  -i, --info            print informtion on the selected task
  -w, --wait            wait for the command to terminate (either oarsub or
                        direct run)

```


All jobs are defined in the config file (by default jobs.ini)

Here is a very simple example 

```ini
[Config]
title=mytitle

[task1]
cmd=echo {title}

```

The [Config] section defines defaults values for all tasks. 
One job is one section in the init file. One the previous example there is only one task name "task1".

Note that the variable cmd has to be defined sice it correspond sto the command line to execute.

You can use simple python templating  for seting a global variable (in this example title) that will be used in another variable. Of course not ciclic redundancy is permited.

To list the available tasks run

```bash
$ ./runexp 
Task list:
	task1
```

You can execute task one by running 

```bash
$ ./runexp task1
mytitle
```
which executes the echo command

For each job one can define one or several variables and their corresponding values. For instance

```ini
[task2]
cmd=echo {i}
varlist=i
i=1:10
```
defines a task that will execute 10 times echo with parameter 1 to 10 :
```bash
$ ./runexp task2
1
2
3
4
5
6
7
8
9
10
```

See the jobs.ini in the repository for more detailed example (multiple variables, OARSUB submissions)


