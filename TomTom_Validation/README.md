# Overview
This repository contains code to help you run Sumo simulations within Jupyter notebooks using TraCI. It also contains the network and configuration files for DFW that we've been working on.

## Directory structure
### Networks
This directory should contain date-named subdirectories. Each date-named subdirectory should contains a sumo network file (.net.xml), an additionals file (.xml) and a configuration file (.sumocfg). At the top level is a README.md that describes the changes/edits/uses of each date-named subdirectory.

Since a network file and it's additionals file must remain somewhat synced (they must use the same edge names for example), it's worth always keeping new versions bundled together inside a directory. We've also chosen to use dates for versioning, hence the date-named directory.
### Notebooks
This is where the Jupyter notebooks live. They use a common module: traciHelper.py. The notebooks all use a .sumocfg file to run the simulation, and it should be easy to update them to point to a new .sumocfg if needed. They also write output files. If the output may be useful to others, consider saving it into the Results directory and updating the repository. Note that running a Sumo simulation also generates a logfile that is saved within this directory. You probably don't need to worry about it unless you think Sumo is doing something weird, then it may have some insights.
### Results
Results files live here.
