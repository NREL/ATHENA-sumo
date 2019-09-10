
# RUN SUMO AND GENERATE OUTPUTS


### Be sure to have all files to run a simulation and make sure $SUMO_HOME is in you path
1. Sample input files can be found the [SUMO_input_files](https://github.com/NREL/ATHENA-siem-sumo/tree/master/Example_Files/SUMO_Input_Files)


## Running SUMO without gui (RUN this to process output files!):

2. Running the simulation without a GUI
```bash
$SUMO_HOME/bin/sumo -n DFW_valid_2.net.xml --additional-files additional_2018-06-11.xml -r trip_2017-12-31.xml  --device.emissions.probability 1 --tripinfo-output trip_output_low.xml --stop-output stop_output_low.xml 
```
### Then convert XML -> CSV
3. Convert Outputs to CSV
```bash
  python $SUMO_HOME/tools/xml/xml2csv.py <FILE.xml>
  
```

### More Output options (data)
4. More options
```bash
  --full-output <FILE> # Full dump of simulation (caution: may be very large)
  
  --vtk-output <FILE>
  
  --fcd-output <FILE>
  
  --amitran-output <FILE>
  
  --vehroute-output <FILE> 
  
  --summary <FILE>
  
  --tripinfo-output <FILE>
  
  
```


### The Above are all possible simulation outputs. Please see documentation for more information on each and to explore other visualizations/output data.

[SUMO output files](https://sumo.dlr.de/wiki/Simulation/Output)

[SUMO visualizations](https://sumo.dlr.de/wiki/Tools/Visualization)


# PROCESS OUTPUTS
1. Make sure you have run a SUMO simulation with outputs to generate. For the data processing, you will need to have run the stops output and trips out with emissions.
2. Once you have completed this, run all the cells in Output_for_objective_function.ipynb
3. This code will create a dictionary of dataframes so that you can pick a given time of day and explore some statistics about the bus routes. For example:
```python
mean_dictionary['gallons']['am']
```
```html
Note: this will output a matrix of all the terminals and any combination of routes between them with their respective fuel consumption in gallons during the AM peak
```
4. For more options than 'gallons' and 'am', use dictionary below:
```python
mean_dictionary{
                'gallons':{
                          'am': DataFrame, # Am peak
                          'pm': DataFrame, # PM peak
                          'mid': DataFrame, # Midday between peaks
                          'op': DataFrame}, # everything else
                'tripinfo_duration': {...},
                'distance_miles':{...}
 deviation_dictionary{
                'gallons':{
                          'am': DataFrame, # Am peak
                          'pm': DataFrame, # PM peak
                          'mid': DataFrame, # Midday between peaks
                          'op': DataFrame}, # everything else
                'tripinfo_duration': {...},
                'distance_miles':{...}

```
5. For specific values you can index the Matrix:
```python
mean_dictionary['gallons']['am']['A']['B']
```
6. Last you can visualize the matrices and trip duration
