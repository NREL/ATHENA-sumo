#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time


# ## Change the parameters below to match your simulation scenarios

# In[8]:

# year = 0 is the original demand from DFW, year 1 is year 0 demand scaled by 3%, year 2 is year 1 demand scaled by 3%, ... 
time_in_hours = 2    # Run time of job on eagle, float
begin_year = 1   # first year to be simulated, integer
end_year = 5      # last eyar to be simulated, integer
demand_file = '2018-3-16.TEST.trips.xml'     # Should be the date of the day you are simulating


# ## Don't change the parameters below

# In[3]:


account = 'athena'    # account allocation on Eagle
sumo_loc = 'SUMO_HOME=/projects/athena/sumo-installation/dist/sumo-git' #Location of SUMO installation on Eagle
number_nodes = end_year - begin_year + 1  # number of nodes to be requested, integer. Should be equal to number of years to be simulated.
scale_factor = 0.03  # Increase in demand per year
job_name='year_'+str(begin_year)+'_'+str(end_year)    # Job name on Eagle, useful for differentiating jobs when running multiple jobs
out_file = 'year_'+str(begin_year)+'_' + str(end_year)+'.log'   # file to log output from simulation runs 


# ## If you set up your work directory as shown in the README, you should not have to change the parameters below

# In[4]:


network_file = '../NetFiles/DFW2.net.xml'   # Relative path to network file from ScriptFiles folder
trip_folder = '../TripFiles/'      # Relative path to trip file folder from ScriptFiles folder
add_file = '../AddFiles/additional_2020-03-25.xml'   # Relative path of additional file from ScriptFiles folder
output_folder = '../output'    # Relative path to output folder from ScriptFiles folder
add_folder = '../AddFiles/'    # Relative path to additional files folder
out_file_prefix = 'get_edge_out_year_'   # prefix of additional file that request output file


# ## Creating the script files

# In[9]:


# First add the instructions for job allocation
if begin_year == end_year: script_file = "run_sim_"+ str(begin_year) + '.slurm'
else: script_file = "run_sim_"+ str(begin_year) + '_' + str(end_year)+'.slurm'

file = open(script_file, "w")
file.write("#!/usr/bin/env bash\n")
file.write("#SBATCH --job-name=year_" + str(begin_year) + '_'+ str(end_year) +'\n')
file.write("#SBATCH --output=sims_" + str(begin_year) + '_'+ str(end_year) +'\n')
file.write("#SBATCH --account=athena\n")
time_string = time.strftime('%H:%M:%S', time.gmtime(time_in_hours*3600))
file.write("#SBATCH --time="+ time_string + "\n")
file.write("#SBATCH --nodes=" + str(number_nodes) + '\n')
file.write("\n")
file.write("export " + sumo_loc + "\n")
file.write("\n")
trip_file = trip_folder + demand_file

# Adding srun commands to execute jobs in parallel
i = 1
for y in range(begin_year, end_year+1):
    scaling= (1+scale_factor)**y
    str_scale = str(round(scaling, 2))

    file.write('srun -N 1 $SUMO_HOME/bin/sumo -n ' + network_file + ' -r ' + trip_file + ' --scale ' + str_scale
               + ' -e 86400 -a ' + add_file + ','+ add_folder +  out_file_prefix + str(y)
           + '.xml' + ' --tripinfo-output ' + output_folder + '/year_' + str(y)+ '_trip_outputs.xml' + 
           ' --eager-insert t --summary ' + output_folder + '/year_' + str(y) + '_summary.xml')
    if end_year > begin_year: file.write(' &\n')
    else: file.write('\n')
    file.write('\n')
    
    
if end_year > begin_year: file.write('wait\n')
file.close()

