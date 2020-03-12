# Semantic Data Management - Laboratory Session 1

## Dependencies

Necessary dependencies for this project are:

```.python
Package         Version
--------------- -------
Faker           4.0.1  
lorem           0.1.1  
neo4j           1.7.6  
neobolt         1.7.16 
neotime         1.7.4  
nltk            3.4.5  
numpy           1.18.1 
pandas          1.0.1  
pip             20.0.2 
python-dateutil 2.8.1  
python-dotenv   0.12.0 
pytz            2019.3 
setuptools      45.2.0 
six             1.14.0 
text-unidecode  1.3    
textblob        0.15.3 
wheel           0.34.2
```

To install them execute:

```
$ pip3 install -r dependencies.txt
```

where `dependencies.txt` is a file that contains dependencies 
mentioned above.

## Part A - Modeling, Loading, Evolving

### A.1 Modeling 

![graph-model](https://i.imgur.com/MsvJhtT.png)

### A.2 Instantiating/Loading

Extract `XML` file from the [DBLP](https://dblp.uni-trier.de/) using
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

A.3 Evolving the graph

![graph-model-evolved](https://i.imgur.com/zNNiYpy.png)