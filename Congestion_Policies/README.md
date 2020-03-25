# This folder has code for creating simulation for different scenarios and congestion policies

## STEP 0: Clone REPO and Setup Enviroment

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

## Step 3: Move Demand to Eagle
Once you have generated your XML trips file, you will need to move it to Eagle and run it on HPC. To do this, you can run the code below. Be sure to **REPLACE {NameOfYourOutputDemand.xml}** with the file name you just generated. [**Master_Function.ipynb**](Master_Function.ipynb) will print the file name as the last line in the notebook.
```linux
scp ../Example_Files/TempInputTrips/{NameOfYourOutputDemand.xml} eagle.hpc.nrel.gov:/scratch/{HPC user name}/path/to/Trips/.

```

## STEP 4: Run SUMO simulation

- Interactive Node
```linux
ssh eagle.hpc.nrel.gov
cd /project/athena/sumo_data/input_files/
srun --time=30 --account=athena --ntasks=1 --pty $SHELL
export SUMO_HOME="/projects/athena/sumo-installation/dist/sumo-git"
$SUMO_HOME/bin/sumo -n DFW2.net.xml --additional-files addition-file -r trips.xml 
```

- As a batch file
```linux
ssh eagle.hpc.nrel.gov
cd /project/athena/sumo_data/inputData/
chmod u+x <YourBatch.batch>
./<YourBatch.batch>
```

## STEP 5: Visualizations 
in progress...
