# SECTION 1: GENERATE DEMAND
1. If you have done step 1 of setting up you enviroment "athena", you can now move on to generating demand
2. in the directory open your terminal and type:
```linux
jupyter notebook
```
3. paste link into chrome browser or use the window that opens automatically for you
4. Run all cells of code
5. In one of the cells you will find TOP 10, BOTTOM 10 and MIDDLE 10 days of volume. These are here to help you decide the type of day you want to run
6. In the cell below "Pick your day of Interest", add your date as a string to the function. Example below:
```python
day, date = pick_day('2017-12-31')
```
```html
Note: this will generate the volume for December 31, 2017
```
7. Continue running cells for visualizations of that particular day
8. To generate the .XML file that SUMO needs to run:
```python
model_to_sumo(day,date,False)
```
```html
Note: "day" and "date" aurguments are already set from above. The third aurgument is 
for a Policy reallocation. "False" is the default and will not run the policy. Other options 
are any float between [0,1]
```
9. After running your .XML will be stored in the input Folder
10. Run last cells to get updated additional XML files for SUMO. These are there to designated the stops and vehicle types.

# SECTION 2: PROCESS OUTPUTS
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
