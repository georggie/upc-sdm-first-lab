# Semantic Data Management - Laboratory Session 1

## Dependencies

Necessary dependencies for this project are:

```.python
lorem==0.1.1
neo4j==1.7.6
neobolt==1.7.16
neotime==1.7.4
nltk==3.4.5
numpy==1.18.1
pandas==1.0.1
python-dateutil==2.8.1
python-dotenv==0.12.0
pytz==2019.3
six==1.14.0
textblob==0.15.3
```

To install them execute:

```
$ pip3 install -r dependencies.txt
```

where `dependencies.txt` is a file that contains dependencies 
mentioned above.

## Part A - Modeling, Loading, Evolving

### A.2 Instantiating/Loading

Firstly, extract `XML` file from the [DBLP](https://dblp.uni-trier.de/) using
[this](https://github.com/ThomHurks/dblp-to-csv) repository. 
Create a folder with the name of the value of an entry `DBLP_SOURCE` (look at
`.env.example` file, default is `resources`). Move all files
that are the result of parsing into that directory. After that
run `extract.py` script (you will need to provide names of three files there). 
The result is two files (`journals.csv` & `conferences.csv`) 
that are placed in the same directory mentioned above.

**Note**: Before going to the loading part move
those two files to `/var/lib/neo4j/import` directory (for Linux).

In order to instantiate/load a graph you need to
run `python` script called `load.py`. After this step
graph should be loaded.



