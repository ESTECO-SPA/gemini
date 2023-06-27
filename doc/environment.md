## How to setup your development environment

### Step 1: Cloning gemini repository + building the root tree

Clone this repository into ```<root_folder>``` (use the name that you prefer)

```commandline
mkdir <root_folder>
cd <root_folder>
git clone git@github.com:ESTECO-SPA/gemini.git
```

### Step 2: Installing ESMINI

There are two options:

##### Downloading executable (**Recommended**)

- Download the latest ESMINI release 2.23.4 ```esmini-demo_<your_os>.zip``` from https://github.com/esmini/esmini/releases/ and extract into the folder `<root_folder>/esmini`. (**Please consider** that the implementation has been based on the ESMINI rev version 6a8cb89. You can download a compiled version for Linux of that revision [here](https://drive.google.com/file/d/14vAQjZJfrkWKuODzIClLpYBiIBPt6gUe/view?usp=sharing)).

#### Build from scratch
- Build ESMINI from scratch (instructions available here: https://esmini.github.io/)

The ESMINI installation folder should be named ```esmini``` and contained into ```<root_folder>```.\
Your folder should be like this:

```commandline
<root_folder>/gemini     <-- it contains  the gemini source code
<root_folder>/esmini     <-- in contains the esmini source files
```

### Step 3: Installing conda + creating the environment

I kindly suggest to install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) which is a free minimal
installer for conda.\
You need to create an enviroment

```commandline
conda create -n gemini python=3.8 
```

and activate it

```commandline
conda activate gemini
```

You are ready to install all the necessary packages:

```commandline
pip3 install python-dotenv
conda install protobuf 
conda install pandas 
conda install matplotlib
conda install -c pytorch pytorch 
pip install scenariogeneration
```

### Step 4: Add osi3 package

You need to manually add the open simulation interface dependency (osi3 package) to your gemini environment.
Please **activate the gemini environment** and then execute the following (from the `<root_folder>`):

```commandline
git clone https://github.com/OpenSimulationInterface/open-simulation-interface.git
cd open-simulation-interface
pip3 install . 
```

For additional information visit the open simulation interface
website ([link](https://opensimulationinterface.github.io/open-simulation-interface/)).

[//]: # (#### python-dotenv & scenariogeneration)

[//]: # ()
[//]: # (```commandline)

[//]: # (pip3 install python-dotenv )

[//]: # (pip3 install scenariogeneration)

[//]: # (```)

### Step 5: Installing PyCharm + creating the environmental file

For this project we recommend to use [PyCharm](https://www.jetbrains.com/pycharm/).

1. You need to create a new PyCharm project based on the gemini folder
2. Set up the Python interpreter to the gemini conda environment (see Step 3)
3. **You need to create a file** named ```.env``` in the gemini folder wit the following content:

#### Linux

```commandline
ESMINI_LIB_PATH = <previous_path>/<root_folder>/esmini/Hello-World_coding-example/libesminiLib.so
ESMINI_RESOURCES_FOLDER = <previous_path>/<root_folder>/esmini/resources
ESMINI_PATH = <previous_path>/<root_folder>/esmini/
DATA_PATH = <previous_path>/<root_folder>/data/  (see step 6)
```

#### Windows

```commandline
ESMINI_LIB_PATH = <previous_path>\<root_folder>\esmini\bin\esminiLib.dll
ESMINI_RESOURCES_FOLDER = <previous_path>\<root_folder>\esmini\resources
ESMINI_PATH = <previous_path>\<root_folder>\esmini\
DATA_PATH =  <previous_path>\<root_folder>\data\ (see step 6)
```

Notice that the address are absolute path so ```<previous_path>``` is referring the first part of the absolute path
pointing the ```root_folder```

### Step 6: download necessary files and set DATA_PATH
To execute the script contained in  you need to download [this](https://github.com/ESTECO-SPA/gemini/blob/main/contribution/analysis/data.zip) zip. 
It contains the data folder that you have to extract in the `<root_folder>` and the xosc folder (you have to copy its content into `esmini/resources/xosc/`).
Read the instruction contained into it. 

## How to run tests

### With PyCharm

Run the "run configuration" named _all tests_.\
Please check that its configuration has the following settings:

- **Target**: script path (with target path: ```<root_folder>/gemini/test```)
- **Python Interpreter:** pointing to the gemini conda environment (see step 3)
- **Working Directory**: ```<root_folder>/gemini```

### With console

Enter in the gemini folder and run the following command 

```commandline
python -m unittest discover -s ./test -t ./
```

## Simulator Shortcut

| key | instruction                           |
|-----|---------------------------------------|
| w   | see geometry                          |
| t   | see only floor                        |
| i   | show information (bottom left string) |
| o   | show origin                           |
| p   | remove scene                          |
| s   | (multiple press) show server info     |
| f   | full screen                           |
| h   | : help                                |
| j   | show trajectory                       |
| l   | light on/off                          |
| ,   | show agent geometry                   |

## Add dependencies
If you need to add some dependency you need to update the gemini.yml env file.
Please use the following command
```commandline
conda env export --no-builds > gemini.yml
```
Symmetrically, to update the conda environment starting from the updated gemini.yml 
file, use the following command:
```commandline
conda env update --file gemini.yml  --prune
```