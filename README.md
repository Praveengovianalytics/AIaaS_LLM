# BTO_LLM_App

This repository constitutes the foundational backend infrastructure for the BrainWave Application. The application is primarily built upon the FastAPI framework to serve as the backbone for its API functionalities. It mandates the use of Python version 3.10.0 or higher to ensure compatibility and optimal performance.

Notably, the application leverages the Langchain library to facilitate the seamless loading of the underlying LLM model, showcasing a commitment to robust and cutting-edge technology integration. This repository serves as the cornerstone for the BrainWave Application's server-side operations, enabling efficient data processing and interaction with the LLM.

## Tools used in this project
* [Poetry](https://towardsdatascience.com/how-to-effortlessly-publish-your-python-package-to-pypi-using-poetry-44b305362f9f): Dependency management - [article](https://mathdatasimplified.com/2023/06/12/poetry-a-better-way-to-manage-python-dependencies/)
* [hydra](https://hydra.cc/): Manage configuration files - [article](https://mathdatasimplified.com/2023/05/25/stop-hard-coding-in-a-data-science-project-use-configuration-files-instead/)
* [pre-commit plugins](https://pre-commit.com/): Automate code reviewing formatting
* [DVC](https://dvc.org/): Data version control - [article](https://mathdatasimplified.com/2023/02/20/introduction-to-dvc-data-version-control-tool-for-machine-learning-projects-2/)
* [pdoc](https://github.com/pdoc3/pdoc): Automatically create an API documentation for your project

## Set up the environment
1. Install [Poetry](https://python-poetry.org/docs/#installation)
2. Set up the environment:
```bash
make env 
```

## Install dependencies
To install all dependencies for this project, run:
```bash
poetry install
```

To install a new package, run:
```bash
poetry add <package-name>
```

## Start Application
To start the application, enter the src directory:

```bash
cd src

```


Then run:
```bash
python main.py --port <port-number>

```


OR

Set Port Number In src/core/settings.py:
```bash
PORT_NUMBER=8000

```

Then run:
```bash
python main.py 

```

Note: Direct Calling Through Args On Running Will Be Prioritised

## Version your data
To track changes to the "data" directory, type:
```bash
dvc add data
```

This command will create the "data.dvc" file, which contains a unique identifier and the location of the data directory in the file system.

To keep track of the data associated with a particular version, commit the "data.dvc" file to Git:
```bash
git add data.dvc
git commit -m "add data"
```

To push the data to remote storage, type:
```bash
dvc push 
```

## Auto-generate API documentation

To auto-generate API document for your project, run:

```bash
make docs
```
