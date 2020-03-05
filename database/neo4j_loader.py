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

    def _load_journals(self):
        print('Loading journals to neo4j ...')
        session = self._driver.session()
        session.run("""
        LOAD CSV WITH HEADERS FROM 'file:///journals.csv' AS row
        MERGE (paper:Paper {id: row.key, title: row.title, abstract: row.abstract, pages: coalesce(row.pages, 38-40), url: coalesce(row.ee, 'unknown')})
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
        MERGE (journal)-[:BELONGS_TO]->(volume)-[:PUBLISHED]->(date)"""
                    )


