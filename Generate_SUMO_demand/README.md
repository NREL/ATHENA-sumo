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
6. To generate demand you will need ot run the notebook (DFW_gen_flow.ipynb)
```linux
jupyter notebook
```
> Once in the notebook, you will want to run all the cells refer to 

7. To deactivate environment:
```linux
conda deactivate 
```

