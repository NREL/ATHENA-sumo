# ATHENA MODELING: SIMULATION WITH SUMO
### Contributors:
Juliette Ugirumurera <Juliette.Ugirumurera@nrel.gov>.
<br>
& Joseph Severino: <Joseph.Severino@nrel.gov>

## THIS IS A CONFIG/ANALYSIS REPO
### Description of REPO
<p>This repo is container for all the code related to modeling DFW airport curbside using SUMO simulator and the pipeline into the infrustructure optimization model. It demonstrates how to install, run and derive useful data from SUMO simulator. We will describe the basic files needed to run a simulation and how those files are generated. The examples provided are a representation of the DFW airport for curbside dropoff and and pickup.</p>

### The following are contained in this repository

File System for ATHENA


- Install_SUMO
     * [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Install_SUMO)
- Generate_SUMO_demand
     * [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand)
     * environment.yml
     * Ipython notebook
- Process_SUMO_outputs
     * [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output)
     * Ipython notebook
- Example_Files
     * Prediction File
     * Folder w/ Sample Inputs
     * Folder w/ Sample OUTPUTS
-	.gitignore
-	README.md

## HOW TO USE THIS REPO

![WorkFlow!](Athena_Workflow.png "How to use this repo")


### 1. Setup Conda Environment
use this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand)  for instructions

### 2. Select day and generate Demand
>use  this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand) for
instructions
### 3. Run SUMO simulation
>use this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output)
### 4. Process Outputs
>use  this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output) for  
instructions
