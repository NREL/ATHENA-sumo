# Contributing

When desiring to contribute to this repository, please first discuss your contribution via issue or email with the owners of this repository. You can then follow the instuctions for forking the repo to include your contribution. Otherwise, if you wish to use the code base and not collaborate, please clone and create new branch.

Joe: <joseph.severino@nrel.gov>
Juliette: <Juliette.Ugirumurera@nrel.gov>


## Forking repo
1. Use the instruction in following link to fork this repo [Instructions](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/fork-a-repo)
2. Make changes locally to code base
3. To contribute: make a pull request to the repo. If there are any merge conflicts, the pull request will be rejected so please resolve any conflicts on your end before requesting us to pull changes.


## Create a new-branch
After creating a branch, check it out locally so that any changes you make will be on that branch.
```bash
git checkout -b BRANCH_NAME
```
> This checks out a branch called BRANCH_NAME based on master, and the -b flag tells Git to create the branch if it doesn’t already exists. Use your name and any other descriptor for branch naming convention.

Once you have made changes locally and would like to push to your branch. Do the following:

```bash
git status 
git add FILES_TO_BE_ADDED
git commit -m "explain what you are adding with concsise detail"
git push -u origin BRANCH_NAME
```
