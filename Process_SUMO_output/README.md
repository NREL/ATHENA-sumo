
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
