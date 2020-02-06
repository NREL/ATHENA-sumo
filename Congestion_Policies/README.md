# This folder has code for creating simulation for different scenarios and congestion policies

## STEP 1: Ensure you have all dependencies

####  predicted demand file: On Eagle under
> ```linux  
> /projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv
> ```

#### And place this file under:
> ```linux  
> scp eagle.hpc.nrel.gov:/projects/athena/sumo_data/predicted_demand/athena_sumo_v1.csv ../Example_Files/athena_sumo_v1.csv
> ```
## STEP 2: Setup Enviroment

> ```git
> conda env create -f AthenaSumoEnviroment.yml 
> conda activate AthenaSumo
> ```

Now are ready do run some code!

## STEP 3: Run Mast Function in <bold> Master_Function.ipynb </bold>
