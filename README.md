# Hack The Bay Challenge 2

## Installing The Application
### Anaconda

#### Anaconda Installation
Please follow [Anaconda's Installation Documentation](https://docs.anaconda.com/anaconda/install/) for your platform

### Python Version
Please make sure you are using Python version 3.8.5. Parts of the code rely on features introducted in some of the most recent versions of Python so this step is key to get the app to work locally. You can download this latest version (as of August 30, 2020) version of Python [here](https://www.python.org/downloads/).

#### Create Environment

There are 2 different environment files - one for Mac and one for Windows - and you should use the one that is specific to your operating system.
After installing Anaconda, navigate to the `src` directory of this repository, and create the Anaconda environment by executing the following command in a terminal:

If you are on Windows, run 
```conda env create -f environment.yml```

If you are on a Mac, run 
```conda env create -f environment_mac.yml```


#### Activate Environment

After creating the Anaconda environment, navigate to the `src` directory of this repository and activate the Anaconda environment by executing the following command in a terminal.
```
conda activate hackthebay
```
-------------------------------------------
## Running The Application
### Starting the Dash Application
After following the installation steps, open the ***Anaconda command prompt***, navigate to the repository's `src` directory, and execute the following command.
```
python index.py
```

### Viewing the Dash Application
After starting the Dash application, open a browser and navigate to [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

-------------------------------------------
## Other
**Helpful Links**

[DevPost HomePage](https://hack-the-bay.devpost.com/)

[HackTheBay GitHub](https://github.com/Hack-the-Bay/hack-the-bay)

-------------------------------------------
## Citations
### Datasets
### Libraries
* *Dash* (1.4.1). (2020). [Web App Data Visualization Framework]. Plotly. https://plotly.com/dash/
* *GeoPandas* (0.8.1). (2020). [Geographical Table Data Processing Framework]. https://geopandas.org/
* *Pandas* (1.0.5). (2020). [Table Data Processing Framework]. https://pandas.pydata.org/
* *Plotly* (4.9.0). (2020). [Data Visualization Framework]. Plotly. https://plotly.com/python/
