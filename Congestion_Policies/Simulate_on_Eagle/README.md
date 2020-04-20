# Running many simulation scenarios on HPC

### 1.  Login into Eagle HPC: 
```bash
ssh username@eagle.hpc.nrel.gov
```

### 2.  Go to athena project space and create a directory for your work (replace <NameOfyourWorkDirectory> with a name for your directory):
```bash
cd /projects/athena/
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

### 4.  Copy network file to your NetFiles folder (Include the '.' at the end command)
```bash
cd NetFiles
cp /projects/athena/sumo_data/input_files/Networks/DFW2.net.xml .
```


### 5.  Copy network additional file to AddFiles folder (Include the '.' at the end command)
```bash
cd ..
cd AddFiles
cp /projects/athena/sumo_data/input_files/AdditionalFiles/additional_2020-03-25.xml .
```

### 6.  Copy output additonal files to AddFiles folder (Include the '.' at the end command)
```bash
cd ..
cd AddFiles
cp /projects/athena/juliette/AddFiles/get_edge_out_year_* .
```

### 7. From local computer,copy generated trip files (generated with Master_Function) into TripFiles folder. Follow the instructions in the [congestion folder](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies).

### 8. From local computer, copy the Create_Script.py script to your ScriptFiles folder from this folder (Simulate_on_Eagle).:
```bash
scp Create_Script.py eagle.hpc.nrel.gov:/projects/athena/<NameOfyourWorkDirectory>/ScriptFiles/
```

### 9.  On Eagle, Open Create_Script.py python scrit, and change the 'time_in_hours', 'begin_year', 'end_year', and 'trip_file_prefix' parameters according to desired simulation years. Script explains values to give for these parameters.

### 10.  On Eagle, run script to generate script to run on Eagle
```bash
cd ScriptFiles
module load conda
python Create_Script.py
```

### 11.  Check if create script file has correct trip files as those you generated: for each srun line in script file, "-r" command should be followed by path to one of your trip files in "TripFiles" folder. Example below uses "emacs" editor, but you can use any other command line editor you like.
```bash
emacs <CREATED SCRIPT FILE>
```

### 12.  Submit script job to Eagle:
```bash
sbatch <name_of_script_file>
```

### 14.  Check status for job with following command. Of command returns line containing: PD means job pending, R means running. If command returns nothing, it means all jobs you submitted to Eagle are done.  
```bash
squeue | grep <eagle username>
```

### 15.  You can also add the following lines under all "#SBATCH" lines in your script file to allow srun to email you when your job start, end, or fails:
```bash
#SBATCH --mail-type=begin,end,fail
#SBATCH --mail-user=user@domain.com
```

### 16.  When the job is done, check if simulations completed successfully. If command below a value greater than 0, then the job was termitted before completion. You will need to edit the script file by increasing the allocation time requested, and resubmit job (go back to step 12).
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
You can also use a convert script file by copying it to your output file:
```bash
cd output
/projects/athena/juliette/output/convert_xml.slurm
```
