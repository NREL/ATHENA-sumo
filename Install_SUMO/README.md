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
