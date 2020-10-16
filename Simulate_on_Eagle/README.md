# Running many simulation scenarios on [Eagle HPC System](https://www.nrel.gov/hpc/eagle-system.html).

### 1.  Login into Eagle HPC. This assumes you already have an account and project allocation on Eagle. 
```bash
ssh username@eagle.hpc.nrel.gov
```

### 2.  Go to your project's space and create a directory for your work (replace <NameOfyourWorkDirectory> with a name for your directory):
```bash
cd /projects/<PROJECT-NAME>/
mkdir <NameOfyourWorkDirectory>
```

### 3.  In your work directory, make a directory for Network files, Trip files, Additional files, simulation script files, and output files :
```bash
cd $NameOfyourDirectory
mkdir NetFiles
mkdir TripFiles
mkdir AddFiles
mkdir ScriptFiles
mkdir output
```

### 4.  Copy a network file from your local computer to your NetFiles folder.
```bash
cd NetFiles
scp ../Example_Files/SUMO_Input_Files/{DFWNetworkFile.xml} eagle.hpc.nrel.gov:/projects/{PROJECT-NAME}/path/to/NetFiles/.
```


### 5.  Copy network additional file to AddFiles folder (Include the '.' at the end command)
```bash
cd ..
cd AddFiles
scp ../Example_Files/SUMO_Input_Files/{DFWAdditionFile.xml} eagle.hpc.nrel.gov:/projects/{PROJECT-NAME}/path/to/AddFiles/.
```

### 6. Generate output additional files by running the [generateEdgesOutXmls.py](https://github.com/NREL/ATHENA-sumo/blob/master/Simulate_on_Eagle/generateEdgesOutXmls.py).
<br>
[generateEdgesOutXmlsWithSubFolder.py] python script(https://github.com/NREL/ATHENA-sumo/blob/master/Simulate_on_Eagle/generateEdgesOutXmlsWithSubFolder.py) generates output additional files with desired subfolder within the output/ folder.


### 7. From local computer,copy generated trip files (generated with Master_Function) into TripFiles folder. Follow the instructions in the [congestion folder](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies).

### 8. Copy the Create_Script.py script from your local computer to your ScriptFiles folder from this folder:
```bash
scp Create_Script.py eagle.hpc.nrel.gov:/projects/athena/<NameOfyourWorkDirectory>/ScriptFiles/
```
Use [Create_Script_Scaling.py](https://github.com/NREL/ATHENA-sumo/blob/master/Simulate_on_Eagle/Create_Script_Scaling.py) script to create many scenarios from one demand file scaled up or down to represent demand growth or decrease.
<br>
Use [Create_Script_inParts.py](https://github.com/NREL/ATHENA-sumo/blob/master/Simulate_on_Eagle/Create_Script_inParts.py) script to run one simulation in mutiple parts. This is useful when you have a simulation that takes more than 4 hours to complete.

### 9.  On Eagle, Open Create_Script.py python, and change the 'time_in_hours', 'begin_year', 'end_year', and 'trip_file_prefix' parameters according to desired simulation years. This Script explains values to give for these parameters.

### 10.  On Eagle, run Create_Script.py to generate bash file to run your simulations on Eagle
```bash
cd ScriptFiles
module load conda
python Create_Script.py
```

### 11.  Check if created bash  file has correct trip files as those you generated: for each srun line in script file, "-r" command should be followed by path to one of your trip files in "TripFiles" folder. Example below uses "emacs" editor, but you can use any other command line editor you like.
```bash
emacs <CREATED BASH FILE>
```

### 12.  Submit bash file to Eagle:
```bash
sbatch <name_of_script_file>
```

### 14.  Check status for job with following command. If command returns a line containing: PD means job pending, R means running. If command returns nothing, it means all jobs you submitted to Eagle are done.  
```bash
squeue | grep <eagle username>
```

### 15.  You can also add the following lines in your bash file to allow srun to email you when your job start, end, or fails:
```bash
#SBATCH --mail-type=begin,end,fail
#SBATCH --mail-user=user@domain.com
```

### 16.  When the job is done, check if the simulations completed successfully. If the command below returns a value greater than 0, then the job was termitted before completion. You will need to edit the bash file by increasing the allocation time requested, and resubmit job (go back to step 12).
```bash
grep -o 'CANCELLED' <LOG FILE> | wc -l
```

### 17.  Convert xml output files to csv:
```bash
cd output
module load conda
export SUMO_HOME=/scratch/jugirumu/projects/sumo/dist/sumo-git
python $SUMO_HOME/tools/xml/xml2csv.py <output xml>
```