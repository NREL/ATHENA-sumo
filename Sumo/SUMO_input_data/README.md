## Running SUMO and generating an Output

#### Open command terminal after installing SUMO
#### Be sure to have all files to run a simulation and make sure $SUMO_HOME is in you path

```bash
  sumo-gui -n <network_file.xml> --additional-files <addition_file.xml> -r <trip/route_file.xml> --emission-output <FILE>
```
#### Then convert XML -> CSV

```bash
  python $SUMO_HOME/tools/xml/xml2csv.py <FILE>
  
```

#### More Output options (data)

```bash
  --full-output <FILE> # Full dump of simulation (caution: may be very large)
  
  --vtk-output <FILE>
  
  --fcd-output <FILE>
  
  --amitran-output <FILE>
  
  --vehroute-output <FILE> 
  
  --summary <FILE>
  
  --tripinfo-output <FILE>
  
  
```

#### The Above are not all possible simulation outputs. Please see documentation for more information on each and to explore other visualizations/output data.

[SUMO output files](https://sumo.dlr.de/wiki/Simulation/Output)

[SUMO visualizations](https://sumo.dlr.de/wiki/Tools/Visualization)


## Running SUMO without gui:

#### same as above, but without "-gui"

```bash
   sumo -n <network_file.xml> --additional-files <addition_file.xml> -r <trip/route_file.xml> --tripinfo-output <FILE>
```
