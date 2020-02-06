# This folder has code for creating simulation for different scenarios and congestion policies

## STEP 1: Ensure you have all dependencies

All of the demand is driven by the CTA predictive model. This demand series is located on **Eagle** if it is not currently contained in the repo. It's location on Eagle is as follows:
```linux  
/projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv
```

#### And place this file under:
To be able to copy htis file from HPC to your local directory you will need to secure copy (scp) this file over to *Example_Files*. The following code will do just that:
```linux  
scp eagle.hpc.nrel.gov:/projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv ../Example_Files/athena_sumo_v1.csv
```
## STEP 2: Setup Enviroment
To have all the packages and appropriate versions to run the code, you need to setup your Conda enviroment from the YAML file contained in this directory. The code is below:
```git
conda env create -f AthenaSumoEnviroment.yml 
conda activate AthenaSumo
```

Now are ready do run some code!

## STEP 3: Run Mast Function in  
>  [**Master_Function.ipynb**](Master_Function.ipynb)

## Step 4: Move Demand to Eagle
in you current directory
```linux
scp ../Example_Files/TempInputTrips/{NameOfYourOutputDemand.xml} eagle.hpc.nrel.gov:/projects/athena/sumo_data/inputData/.
```

## STEP 5: Run SUMO simulation

- Interactive Node
```linux
ssh eagle.hpc.nrel.gov
cd /project/athena/sumo_data/inputData/
srun --time=30 --account=athena --ntasks=1 --pty $SHELL
export SUMO_HOME="Something here"
sumo -n DFW2.net.xml --additional-files addition-file -r trips.xml 
```

- As a batch file
```linux
ssh eagle.hpc.nrel.gov
cd /project/athena/sumo_data/inputData/
chmod u+x <YourBatch.batch>
./<YourBatch.batch>
```

## STEP 6: 
