# Semantic Data Management - Laboratory Session 1

This project is the solution of the first laboratory session 
in the subject [Semantic Data Management](https://learnsql2.fib.upc.edu/moodle/) 
([UPC Universitat Politècnica de Catalunya](https://www.upc.edu/en))  

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

This exercise is about modeling graph data for a certain domain. The main goal is to develop
your skills on modeling and instantiating graph data.

### A.1 Modeling 

The picture below represents the proposed solution for the domain 
in the task. Two main criteria for deriving such a model are
the optimization of queries in part B, and correct semantic modeling
of a domain. 

![graph-model](https://i.imgur.com/MsvJhtT.png)

> A paper can be written by many authors, however only one of them acts as corresponding
author...When a paper is submitted to a conference or a journal, the conference chair or the journal editor assigns a set
of reviewers (typically three) to each paper. Reviewers are scientists and therefore they are
relevant authors (i.e., published many papers in relevant conferences or journals).

From these requirements we derived three relationships between `Author`(s) and `ScientificPaper`(s):

* `Author` IS LEAD AUTHOR of a `ScientificPaper`
* `Author` IS CO-AUTHOR of a `ScientificPaper`
* `Author` REVIEWS other `ScientificPaper` (in this phase you can track for 
whom they did review by further following edges from scientific paper to 
either journal or proceeding of a conference or a workshop)

> A paper can be cited by another paper (meaning their content is related). A paper relates to one or more topics through the concept of keywords. Keywords are used by
readers to quickly identify the main topics discussed in the paper. 

So, a scientific paper is related to another paper by means of citations. 
This is a perfect candidate for a recursive relationship. 
In addition, the paper mentions certain keywords that we extracted as 
a separate vertex because of reusability (many other papers will mention 
the same keyword) and readability (semantic). 

* `ScientificPaper` CITES other `ScientificPaper`
* `ScientificPaper` MENTIONS some `Keyword`

> In this domain, authors write research articles that can be published as scientific papers (papers for short) in the proceedings of a conference/workshop (a conference is a well-established forum while a workshop
is typically associated to new trends still being explored), or in a journal. A proceeding is
a published record which includes all the papers presented in the conference/workshop. A
conference/workshop is organized in terms of editions. Each edition of a conference is held
in a given city (venue) at a specific period of time of a given year. Oppositely, journals do
not hold joint meeting events and, like a magazine, a journal publishes accepted papers in
terms of volumes. There can be various volumes of a journal per year.

From this description, we derived two paths for a scientific paper: 

* `ScientificPaper` is PUBLISHED IN a `Journal` which BELONGS TO as 
`Volume` which is further ISSUED in a certain `Year`.

*  `ScientificPaper` IS IN a `Proceeding` OF A `Conference` | `Workshop` 
that HAS `Edition` that HAPPENED in a certain `Year`.

This modeling decision is pretty clear. It models all domain requirements 
without extra overhead vertices or edges. 
It is simple and extremely easy to understand.

Because queries in B do not touch venues, and time period of a given year 
when the conference|workshop was held we decided to put all edition 
information like country, city, a period of the year in `Edition` vertex. 
There will be repeated information such as country property, 
but this does not cause much concern.

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