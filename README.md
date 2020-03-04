# Semantic Data Management - Labaratory Session 1

## Part A - Modeling, Loading, Evolving

### A.2 Instantiating/Loading

In order to instantiate/load the graph you first need to
run `python` script called `dblp-extractor.py`. But before
running the script it is advised to first create virtual 
environment using command:

```
$ virtualenv venv
```

Inside `src` directory there is a file called `dependencies.txt`
that shows python dependencies for this project that need
to be satisfied. Execute:

```
$ source venv/bin/activate
$ pip3 install -r src/dependencies.txt
```

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



