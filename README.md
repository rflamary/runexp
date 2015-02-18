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
All jobs are defined in the config file (by default jobs.ini)

Here is a very simple example 

```ini

[Config]
title=coucou

[task1]
cmd=echo {title}

```

The [Config] section defines defaults values for all tasks. 
One job is one section in the init file. One the previous example there is only one task name "task1".





For each job one can define one or several variables and their corresponding values

#### Sort example


