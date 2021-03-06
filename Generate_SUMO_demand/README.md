# SETUP CONDA ENVIRONMENT
1. In your terminal load  environment.yml file
```linux
conda env create -f environment.yml
```
2. In terminal, check to see if envirment was created
```linux
conda env list
```
3. If installed correctly you will see "athena" as one of your environments
4. Activate "athena" environment
```linux
conda activate athena
```
5. It should look something like this in your terminal: 
```linux
(athena) jseverin-33734s:ATHENA-siem-sumo jseverin$
```
6. To deactivate environment:
```linux
conda deactivate 
```
# GENERATE DEMAND
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
