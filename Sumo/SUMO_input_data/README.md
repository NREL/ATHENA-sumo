# Running SUMO and generating an Output

### Open command terminal after installing SUMO
```html
if SUMO is not installed please refer to the link below for installation
```
1. MAC users: [SUMO for MACs](https://sumo.dlr.de/docs/Installing/MacOS_Build.html)
      * If you have access to NREL GitHub use this [MAC install](https://github.nrel.gov/jseverin/Sumo/blob/master/README.md)
2. Windows users: [SUMO for Windows](http://sumo.dlr.de/docs/Installing.html)

### Be sure to have all files to run a simulation and make sure $SUMO_HOME is in you path
3. Running the simulation with a GUI
```bash
  sumo-gui -n <network_file.xml> --additional-files <addition_file.xml> -r <trip/route_file.xml> --emission-output <FILE>
```

## Running SUMO without gui (RUN this to process Bus route outputs!):

4. Running the simulation without a GUI
```bash
  $SUMO_HOME/bin/sumo -n DFW_valid_2.net.xml --additional-files additional_custom.xml -r Bus_and_curb_high_Aug-27-19.xml --step-length 0.25 --time-to-teleport 500 --device.emissions.probability 1 --summary summary.xml --tripinfo-output tripout.xml --stop-output stop_output.xml --eager-insert t
```
### Then convert XML -> CSV
5. Convert Outputs to CSV
```bash
  python $SUMO_HOME/tools/xml/xml2csv.py <FILE>
  
```

### More Output options (data)
6. More options
```bash
  --full-output <FILE> # Full dump of simulation (caution: may be very large)
  
  --vtk-output <FILE>
  
  --fcd-output <FILE>
  
  --amitran-output <FILE>
  
  --vehroute-output <FILE> 
  
  --summary <FILE>
  
  --tripinfo-output <FILE>
  
  
```

### Generating vehicle trip information including stop durations 
7. Same as above with GUI
```bash
$SUMO_HOME/bin/sumo-gui -n DFW_valid_2.net.xml --additional-files additional_custom.xml -r Bus_and_curb_high_Aug-27-19.xml --step-length 0.25 --time-to-teleport 500 --device.emissions.probability 1 --summary summary.xml --tripinfo-output tripout.xml --stop-output stop_output.xml --eager-insert t
```

### The Above are all possible simulation outputs. Please see documentation for more information on each and to explore other visualizations/output data.

[SUMO output files](https://sumo.dlr.de/wiki/Simulation/Output)

[SUMO visualizations](https://sumo.dlr.de/wiki/Tools/Visualization)
