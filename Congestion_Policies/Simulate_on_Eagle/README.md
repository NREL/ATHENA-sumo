# Running many simulation scenarios on HPC

### First, make sure you have an Eagle HPC account. If not, [request one](https://www.nrel.gov/hpc/user-accounts.html) and request to be added to the Athena project allocation.

1. Login into Eagle HPC: 
```bash
ssh username@eagle.hpc.nrel.gov
```

2. Go to athena project space and create a directory for your work (replace $NameOfyourDirectory with a name for your directory):
```bash
cd /projects/athena/
mkdir $NameOfyourDirectory
```

3. In your work directory, make a directory for Network files, Trip files, Additional files, simulation script files, and output files :
```bash
cd $NameOfyourDirectory
mkdir NetFiles
mkdir TripFiles
mkdir AddFiles
mkdir ScriptFiles
mkdir output
```

4. Copy network file to your NetFiles folder (Include the '.' at the end command)
```bash
cd NetFiles
cp /projects/athena/sumo_data/input_files/Networks/DFW2.net.xml .
```


5. Copy network additional file to AddFiles folder (Include the '.' at the end command)
```bash
cd ..
cd AddFiles
cp /projects/athena/sumo_data/input_files/AdditionalFiles/additional_2020-03-25.xml .
```

6. Copy output additonal files to AddFiles folder (Include the '.' at the end command)
```bash
cd ..
cd AddFiles
cp /projects/athena/juliette/AddFiles/get_edge_out_year_* .
```

7. Copy generated trip files (generated with Master_Function) into TripFiles folder. Follow the instructions in the [congestion policy repository](https://github.com/NREL/ATHENA-sumo/tree/master/Congestion_Policies).

8.Open Create_Script.py python scrit, and change the 'time_in_hours', 'begin_year', 'end_year', and 'trip_file_prefix' parameters according to desired simulation years. Script explains values to give for these parameters.

9. Run script to generate script to run on Eagle
```bash
cd ScriptFiles
module load conda
python Create_Script.py
```

10. Submit script job to Eagle:
```bash
sbatch <name_of_script_file>
```

11. Check status for job with:
```bash
squeue | grep <eagle username>
```

12. When the job is done, check if simulations completed successfully.
```bash
tail -n 5 year_<begin_year>_<end_year>.log
```
If command above returns text containig ' ', the job was terminated before completing. You will need to edit the script file by increasing the allocation time requested, and resubmit job (go back to step 10).

13. Convert xml output files to csv:
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