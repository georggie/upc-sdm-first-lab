import os
from contextlib import redirect_stderr

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
        self._generate_random_citations()
        self._generate_random_reviewers()

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
                MERGE (paper:ScientificPaper {key: row.key, title: row.title, abstract: row.abstract, 
                       pages: coalesce(row.pages, 38-40), url: row.ee})
                MERGE (author:Author {name: row.author})
                MERGE (author)-[:IS_LEAD_AUTHOR]->(paper)
                WITH row, author, paper
                WHERE row.coauthors IS NOT NULL
                UNWIND split(row.coauthors, '|') AS co_author
                MERGE (coauthor:Author {name: co_author})
                MERGE (paper)<-[:IS_CO_AUTHOR]-(coauthor)
                WITH row, paper
                UNWIND split(row.keywords, '|') AS keywrd
                MERGE (keyword:Keyword {name: keywrd})
                MERGE (paper)-[:MENTIONES]->(keyword)
                WITH row, paper
                MERGE (journal:Journal {name: row.journal})
                MERGE (paper)-[:PUBLISHED_IN]->(journal)
                WITH row, journal
                MERGE (date:Year {year: row.year})<-[:ISSUED]-(volume:Volume {number: row.volume})
                MERGE (journal)-[:BELONGS_TO]->(volume)
            """)
        except Exception as exception:
            print("Exception => ", exception)

    def _load_conferences_and_workshops(self):
        """
        Load conferences and journals to the graph database
        :return: void
        """
        try:
            print('Loading conferences to neo4j ...')
            session = self._driver.session()
            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///conferences.csv' AS row
                MERGE (paper:ScientificPaper {id: row.key_x, title: row.title_x, abstract: row.abstract, 
                       pages: row.pages_x, url: row.ee_x})
                MERGE (author:Author {name: row.author_x})
                MERGE (author)-[:IS_LEAD_AUTHOR]->(paper)
                WITH  row, author, paper
                WHERE row.coauthors IS NOT NULL
                UNWIND split(row.coauthors, '|') AS co_author
                MERGE (coauthor:Author {name: co_author})
                MERGE (paper)<-[:IS_CO_AUTHOR]-(coauthor)
                WITH  row, paper
                UNWIND split(row.keywords, '|') AS keywrd
                MERGE (keyword:Keyword {name: keywrd})
                MERGE (paper)-[:MENTIONES]->(keyword)
                WITH  row, paper
                MERGE (proceeding:Proceeding {key: row.key_y, isbn: row.isbn, url: row.ee_y, 
                       published: row.publisher, series: row.series})
                MERGE (paper)-[:IS_IN]->(proceeding)
                WITH  row, proceeding
                WHERE SPLIT(row.title_y, "|")[5] = 'False'
                MERGE (conf:Conference{name: SPLIT(row.title_y, "|")[0]})<-[:OF_A]-(proceeding)
                MERGE (conf)-[:HAS]->(edition:Edition {city: SPLIT(row.title_y, "|")[1], country: SPLIT(row.title_y, "|")[2], period: SPLIT(row.title_y, "|")[3]})
                MERGE (edition)-[:HAPPENED]-(date: Year {year: SPLIT(row.title_y, "|")[4]})
            """)

            print('Loading workshops to neo4j ...')
            session = self._driver.session()

            session.run("""
                LOAD CSV WITH HEADERS FROM 'file:///conferences.csv' AS row
                MERGE (paper:ScientificPaper {key: row.key_x, title: row.title_x, abstract: row.abstract, 
                       pages: row.pages_x, url: row.ee_x})
                MERGE (author:Author {name: row.author_x})
                MERGE (author)-[:IS_LEAD_AUTHOR]->(paper)
                WITH  row, author, paper
                WHERE row.coauthors IS NOT NULL
                UNWIND split(row.coauthors, '|') AS co_author
                MERGE (coauthor:Author {name: co_author})
                MERGE (paper)<-[:IS_CO_AUTHOR]-(coauthor)
                WITH  row, paper
                UNWIND split(row.keywords, '|') AS keywrd
                MERGE (keyword:Keyword {name: keywrd})
                MERGE (paper)-[:MENTIONES]->(keyword)
                WITH  row, paper
                MERGE (proceeding:Proceeding {key: row.key_y, isbn: row.isbn, url: row.ee_y, published: row.publisher, series: row.series})
                MERGE (paper)-[:IS_IN]->(proceeding)
                WITH  row, proceeding
                WHERE SPLIT(row.title_y, "|")[5] = 'True'
                MERGE (conf:Workshop{name: SPLIT(row.title_y, "|")[0]})<-[:OF_A]-(proceeding)
                MERGE (conf)-[:HAS]->(edition:Edition {city: SPLIT(row.title_y, "|")[1], country: SPLIT(row.title_y, "|")[2], period: SPLIT(row.title_y, "|")[3]})
                MERGE (edition)-[:HAPPENED]-(date: Year {year: SPLIT(row.title_y, "|")[4]})
            """)
        except Exception as exception:
            print("Exception => ", exception)

    def _generate_random_citations(self):
        """
        Generate random citations between scientific papers
        :return: void
        """
        print('Generating random citations between papers ...')
        session = self._driver.session()

        session.run("""
            MATCH (scp1:ScientificPaper), (scp2:ScientificPaper)
            WITH scp1, scp2
            WHERE rand() < 0.1 AND scp1 <> scp2
            MERGE (scp1)-[:CITES]->(scp2)
        """)

    def _generate_random_reviewers(self):
        """
        Generate `random` reviewers for papers
        :return: void
        """
        print('Generating random reviewers for papers ...')
        session = self._driver.session()

        session.run("""
            MATCH (scientificPaper:ScientificPaper)-[:MENTIONES]->(keyword:Keyword),
            (author:Author)-[:IS_LEAD_AUTHOR]->(:ScientificPaper)-[:MENTIONES]->(keyword)
            WHERE NOT EXISTS ((author)--(scientificPaper))
            WITH scientificPaper, author, rand() as randomNumber
            ORDER BY randomNumber
            WITH scientificPaper, collect(DISTINCT author)[0..3] as reviewers
            UNWIND(reviewers) as reviewer
            MERGE (scientificPaper)<-[:REVIEWS]-(reviewer)
        """)

    def evolve(self):
        """

        :return:
        """
        print('Evolving the graph ...')

        session = self._driver.session()

        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///reviews.csv' AS row
            WITH row
            MATCH (author:Author {name: row.author})-[rev:REVIEWS]->(scientificPaper:ScientificPaper {title: row.paper})
            SET rev += {comment: row.comment, decision: row.decision, affiliation: row.affiliation, organization: row.organization}
            WITH author, rev, scientificPaper
            MATCH (author:Author)-[rev:REVIEWS]->(scientificPaper:ScientificPaper)-[:IS_IN|:PUBLISHED_IN]->(genericNode)
            MERGE (revn:REVIEW {comment: rev.comment, decision: rev.decision})
            MERGE (author)-[:DOES]->(revn)
            MERGE (revn)-[:ON]->(scientificPaper)
            MERGE (revn)-[:FOR]->(genericNode)
            MERGE (:Organization {name: rev.affiliation})<-[:AFFILIATION {type: rev.organization}]-(author)
            DELETE rev
        """)

    def evolver_helper(self):
        """
        Helper function used in graph evolving
        :return: list of lists
        """
        data = []
        session = self._driver.session()

        results = session.run("""
            MATCH (author:Author)-[rev:REVIEWS]->(scientificPaper:ScientificPaper)
            RETURN author, scientificPaper
        """)

        for item in results:
            value = dict(item['author'])['name']
            key = dict(item['scientificPaper'])['title']
            data.append([value, key])

        return data

