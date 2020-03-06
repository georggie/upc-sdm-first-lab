import os
import settings
from neo4j import GraphDatabase


class Neo4JLoader(object):

    def __init__(self):
        """
        Neo4jLoader constructor
        """
        self._driver = GraphDatabase.driver(os.getenv('DB_URI'),
                                            auth=(os.getenv('DB_USER'), os.getenv('DB_PASSWORD')), encrypted=False)

    def load(self):
        """
        Load graph database extracted from the dblp.xml
        :return: void
        """
        self._load_journals()
        self._load_conferences_and_workshops()

    def _load_journals(self):
        """
        Load journals to the graph database
        :return: void
        """
        print('Loading journals to neo4j ...')
        try:
            session = self._driver.session()
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///journals.csv' AS row
                MERGE (paper:Paper {id: row.key, title: row.title, abstract: row.abstract, 
                       pages: coalesce(row.pages, 38-40), url: coalesce(row.ee, 'Unknown')})
                MERGE (author:Author {name: row.author})
                MERGE (author)-[:IS_LEAD_AUTHOR]->(paper)
                WITH row, author, paper
                WHERE row.coauthors IS NOT NULL
                UNWIND split(row.coauthors, '|') AS co_author
                MERGE (coauthor:Author {name: co_author})
                MERGE (paper)<-[:WRITES]-(coauthor)
                WITH row, paper
                UNWIND split(row.keywords, '|') AS keywrd
                MERGE (keyword:Keyword {name: keywrd})
                MERGE (paper)-[:MENTIONES]->(keyword)
                WITH row, paper
                MERGE (journal:Journal {name: row.journal})
                MERGE (paper)-[:PUBLISHED_IN]->(journal)
                WITH row, journal
                MERGE (volume:Volume {edition: row.volume})
                MERGE (date:Date {year: row.year})
                MERGE (journal)-[:BELONGS_TO]->(volume)-[:PUBLISHED]->(date)
            """)
        except Exception as exception:
            print("Exception => ", exception)

    def _load_conferences_and_workshops(self):
        """
        Load conferences and journals to the graph database
        :return: void
        """
        print('Loading conferences to neo4j ...')
        try:
            session = self._driver.session()
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///conferences.csv' AS row
                MERGE (paper:Paper {id: row.key_x, title: row.title_x, abstract: row.abstract, 
                       pages: coalesce(row.pages_x, 38-40), url: coalesce(row.ee_x, 'Unknown')})
                MERGE (author:Author {name: row.author_x})
                MERGE (author)-[:IS_LEAD_AUTHOR]->(paper)
                WITH row, author, paper
                WHERE row.coauthors IS NOT NULL
                UNWIND split(row.coauthors, '|') AS co_author
                MERGE (coauthor:Author {name: co_author})
                MERGE (paper)<-[:WRITES]-(coauthor)
                WITH row, paper
                UNWIND split(row.keywords, '|') AS keywrd
                MERGE (keyword:Keyword {name: keywrd})
                MERGE (paper)-[:MENTIONES]->(keyword)
                WITH row, paper
                MERGE (proceeding:Proceeding {id: row.key_y, isbn: coalesce(row.isbn, 'Unknown'), url: coalesce(row.ee_y, 'Unknown'), 
                       published: row.publisher, series: coalesce(row.series, 'Unknown')})
                MERGE (paper)-[:IS_IN]->(proceeding)
                WITH row, SPLIT(row.title_y, "|") AS words, proceeding
                WHERE words[5] = 'False'
                MERGE (conf:Conference{name: words[0]})<-[:OF_A]-(proceeding)
                MERGE (conf)-[:HAS]->(edition:Edition {place: words[1], country: words[2], period: words[3]})
                MERGE (edition)-[:HAPPENED]-(date: Date {year: words[4]})
                WITH SPLIT(row.title_y, "|") AS words, proceeding
                WHERE words[5] = 'True'
                MERGE (work:Workshop{name: words[0]})<-[:OF_A]-(proceeding)
                MERGE (work)-[:HAS]->(edition:Edition {place: words[1], country: words[2], period: words[3]})
                MERGE (edition)-[:HAPPENED]-(date: Date {year: words[4]})
            """)
        except Exception as exception:
            print("Exception => ", exception)


