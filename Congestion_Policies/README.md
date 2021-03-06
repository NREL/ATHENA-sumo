# This folder has code for creating simulation for different scenarios and congestion policies
> Click on the links below to skip to your respective step.
- [**STEP 0: Clone Repo & Setup Env**](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/README.md#step-0-clone-repo-and-setup-enviroment)
- [**STEP 1: Ensure Dependencies**](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/README.md#step-1-ensure-you-have-all-dependencies)
- [**STEP 2: Run Master Function**](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/README.md#step-2-run-master-function)
- [**STEP 3: Simulate policy scenario on personal computer**](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/README.md#step-3-simulate-policy-scenario-on-personal-computer)
- [**STEP 4: Simulate policy scenario on HPC**](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies#step-4-simulate-policy-scenarion-on-HPC)
- [**STEP 5: Visualize Outputs**](https://github.com/NREL/ATHENA-sumo/blob/master/Congestion_Policies/README.md#step-5-visualizations)
## STEP 0: Clone REPO and Setup Enviroment
> NOTE: Ensure this is done in a local enviroment – not on Eagle.

In a directory that you want ATHENA-Sumo to be:
```linux  
git clone https://github.com/NREL/ATHENA-sumo.git
cd ATHENA-sumo
conda env create -f environment.yml 
conda activate athena_sumo 
```
Once you have activated ```athena_sumo``` environment you will ```cd``` into ```Congestion_Policies```:

```git
cd Congestion_Policies/
jupyter notebook
```
> NOTE: this will ensure your notebook is in the correct kernal. If not, change your kernal in the notebook to reflect the environment you just created.



## STEP 1: Ensure you have all dependencies

All of the demand is driven by the CTA predictive model. This demand timeseries should be in this repo. However, if it is not (skip to STEP 2 if you have it), there is a copy on **Eagle**. It's location on Eagle is as follows:
```linux  
/projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv
```

To be able to copy this file from HPC to your local directory you will need to secure copy (scp) this file over to *Example_Files*. If you are in Congestion_Policies directory, the following code will do just that:
```linux  
scp eagle.hpc.nrel.gov:/projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv ../Example_Files/athena_sumo_v1.csv
```

## STEP 2: Run Master Function   
This is the .ipynb that generates the Trips demand file. Parameters are explained in notebook.
>  [**Master_Function.ipynb**](Master_Function.ipynb)

## Step 3: Simulate policy scenario on personal computer
> Use [these instructions](https://github.com/NREL/ATHENA-sumo/tree/master/Process_SUMO_output)

## STEP 4: Simulate policy scenarion on HPC
- Move Demand to HPC
Once you have generated your XML trips file, you will need to move it to Eagle and run it on HPC. To do this, you can run the code below. Be sure to **REPLACE {NameOfYourOutputDemand.xml}** with the file name you just generated. [**Master_Function.ipynb**](Master_Function.ipynb) will print the file name as the last line in the notebook.
```linux
scp ../Example_Files/TempInputTrips/{NameOfYourOutputDemand.xml} eagle.hpc.nrel.gov:/scratch/{HPC user name}/path/to/Trips/.

```

- Run on Interactive Node example
```linux
ssh eagle.hpc.nrel.gov
cd /scratch/{HPC_user_name}/path/to/run/Sumo
srun --time=30 --account=athena --partition=debug --ntasks=1 --pty $SHELL
export SUMO_HOME="/projects/athena/sumo-installation/dist/sumo-git"
$SUMO_HOME/bin/sumo -n Network/DFW2.net.xml --additional-files Additional_Files/additional_2019-12-11.xml -r Trips/2018-1-2.High.trips.xml --summary summary.xml --eager-insert t
```

- Run as a batch file 
```linux
ssh eagle.hpc.nrel.gov
cd /scratch/{HPC_user_name}/path/to/run/Sumo
chmod u+x <YourBatch.batch>
./<YourBatch.batch>
```
Example batch file:
```linux
#!/bin/bash
#SBATCH --output=DFW_sim # slurm name
#SBATCH --job-name=JoeSim # job name
#SBATCH --ntasks=1 # Tasks to be run
#SBATCH --nodes=1  # Run the tasks on the same node
#SBATCH --time=100   # Required,
#SBATCH --account=athena # Required
#SBATCH --partition=short

export SUMO_HOME="/projects/athena/sumo-installation/dist/sumo-git"

$SUMO_HOME/bin/sumo -n Network/DFW2.net.xml --additional-files Additional_Files/additional_2019-12-11.xml -r Trips/2018-1-2.High.trips.xml --summary Output/summary.xml  --eager-insert t

python $SUMO_HOME/tools/xml/xml2csv.py Output/summary.xml


```

Additional outputs include: [edge-level traffic measures](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Traffic_Measures.html) and [edge-level emission measures](https://sumo.dlr.de/docs/Simulation/Output/Lane-_or_Edge-based_Emissions_Measures.html).

## STEP 5: Visualizations 
 Visualize one or multiple scenarios from different sumo simulations using the sumo output files (edge-based traffic, edge-based emissions, summary files & trip-based outputs). Single scenario visuals include mode choice graphs, emissions aggregated metrics, and traffic flow scatter plots. While multiple scenarios are compared on a timeseries basis for a given column from edge-based outputs. Refer to the notebook [plotSumoCongestion.ipynb](https://github.com/NREL/ATHENA-sumo/blob/JU_branch/Congestion_Policies/plotSumoCongestion.ipynb) to generate these plots.
