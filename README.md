# ATHENA MODELING: SIMULATION WITH SUMO
### Contributors:
Juliette Ugirumurera <jugirumu@nrel.gov>.
<br>
 Joseph Severino: <Joseph.Severino@nrel.gov>
<br>
Monte Lunacek: <Monte.Lunacek@nrel.gov>
<br>
Yanbo Ge: <Yanbo.Ge@nrel.gov>
<br>
Qichao Wang: <Qichao.Wang@nrel.gov>


## THIS IS A CONFIG/ANALYSIS REPO
### Description of REPO
<p>This repo is contains all the code related to modeling the Dallas-Fort Worth International Airport (DFW) curbside (CTA modeling) using SUMO simulator. It demonstrates how to install, run and derive useful data from SUMO simulations. We will describe the basic files needed to run a simulation and how those files are generated.The repository also has code for generating simulations representing different traffic managment policies for DFW and simulating those policies on personal computer or on NREL's Eagle supercomputer. The examples provided are a representation of the DFW airport for curbside dropoff and and pickup.</p>

### The following are contained in this repository

File System for ATHENA SUMO


- Install_SUMO
     * [README.md](https://github.com/NREL/ATHENA-sumo/tree/master/Install_SUMO)
- Generate_SUMO_demand
     * [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand)
     * environment.yml
     * Ipython notebook
- Process_SUMO_outputs
     * [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output)
     * Ipython notebook

- Congestion_Policies
     * [README.md](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies)
     * Simulate_on_Eagle folder with instructions on how to simulate on [Eagle Supercomputer](https://www.nrel.gov/hpc/eagle-system.html).
     * Master_Function.ipynb: main notebook for generating simulations for different congestion policies
     * Ipython notebooks used by the Master_Function.ipynb notebooks
     * Ipython notebooks to test the functionality of Master_Function.ipynb
- Simulate_on_Eagle:
     * [README.md](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies)
     * Create_Script.ipynb Ipython notebook for creating batch script files for running SUMO simulations on Eagle supercomputer
     * Create_Script*.py python scripts to create batch files for running SUMO simulations on Eagle
     * generateEdges*.py scripts to create SUMO xml files to get outputs from SUMO simulations
- Example_Files
     * Prediction File
     * Folder w/ Sample Inputs
     * Folder w/ Sample OUTPUTS
-	.gitignore
-	README.md

## HOW TO - GENERATE A SUMO SIMULATION
![WorkFlow!](Athena_Workflow.png "How to use this repo")


### 1. Setup Conda Environment
> use this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand)  for instructions

### 2. Select day and generate Demand
> use  this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Generate_SUMO_demand) for
instructions
### 3. Run SUMO simulation - this steps SUMO has already been installed as shown above
> use this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output)
### 4. Process Outputs
> use  this [README.md](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Process_SUMO_output) for  
instructions

## HOW TO - GENERATE A CONGESTION POLICY SIMULATION
![Master_function!](Master_Func_Workflow.png "How to generate congestion policy scenarion")

### 1. Generate a congestion policy by running the [Master_Function.ipynb](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/Master_Function.ipynb) notebook. This results in a SUMO route file that encodes the congestion policy. 
> use this [README.md](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies)  for 
instructions

### 2. Simulate the congestion policy scenario to evaluate the policy:
- This can be done by running SUMO on personal computer using [these instruction](https://github.com/NREL/ATHENA-sumo/tree/master/Process_SUMO_output).
- Or by generating many route files with step 1 to run many simulations in parallel on NREL's HPC system using [these instructions](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies/Simulate_on_Eagle).

