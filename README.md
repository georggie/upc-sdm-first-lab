# Semantic Data Management - Labaratory Session 1

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

where `dependencies.txt` is file that contains dependencies from
above.

## Part A - Modeling, Loading, Evolving

### A.2 Instantiating/Loading

In order to instantiate/load the graph you first need to
run `python` script called `extract.py`. 

Extract XML file from the [DBLP](https://dblp.uni-trier.de/) using
[this](https://github.com/ThomHurks/dblp-to-csv) repository. 
Create folder `dumps` inside the src directory and put there the 
output of parsing (you can name folder however you want but then you need
to fix `SOURCE_PATH` in python script). 

Position to the `src` directory and execute:

```
$ python3 dblp-extractor.py
```

The output will be inside `src/main/resources`. You can 
control the path of the input and output files using the
global variables from the `dblp-extractor.py` file.



