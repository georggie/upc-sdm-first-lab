import os
import settings
from neo4j import GraphDatabase


class Neo4JExecutor(object):

    def __init__(self):
        """
        Neo4jLoader constructor
        """
        self._driver = GraphDatabase.driver(os.getenv('DB_URI'),
                                            auth=(os.getenv('DB_USER'), os.getenv('DB_PASSWORD')), encrypted=False)

    def h_index(self):
        """
        Finds H-index of authors in the graph
        :return:
        """
        session = self._driver.session()

        result = session.run("""
                MATCH (author:Author)-[:IS_LEAD_AUTHOR|:IS_CO_AUTHOR]->(scientificPaper:ScientificPaper)<-[:CITES]-(citatingPaper:ScientificPaper)
                WITH author, scientificPaper, count(citatingPaper) as numberOfCitations
                ORDER BY author, numberOfCitations DESC
                WITH author, collect(numberOfCitations) as orderedCitations
                UNWIND range(0, size(orderedCitations)-1) as arrayIndex
                WITH author, arrayIndex as key, orderedCitations[arrayIndex] as value, size(orderedCitations) as arrayLength
                WITH
                CASE
                WHEN key > value THEN key-1
                ELSE arrayLength END AS result, author
                RETURN author, min(result) as hindex
            """)

        for record in result:
            print(f"{record['author']['name']} => h-index = {record['hindex']}")

    def top3_papers_of_each_conferences(self):
        """
        Finds top 3 papers of each conference in terms of citations
        :return:
        """
        session = self._driver.session()

        result = session.run("""
                MATCH (scientificPaper:ScientificPaper)-[:IS_IN]->(:Proceeding)-[:OF_A]->(conference:Conference),
                (scientificPaper)<-[:CITES]-(citingPaper:ScientificPaper)
                WITH conference, scientificPaper, count(citingPaper) AS numberOfCitations
                ORDER BY conference, numberOfCitations DESC
                WITH conference, collect(scientificPaper) as allPapers, collect(numberOfCitations) as allCitations
                WITH conference, allPapers[0..3] as a, allCitations[0..3] as b
                UNWIND(range(0, 2)) as indexKey
                RETURN conference, a[indexKey] as paper, b[indexKey] as numOfCitations
            """)

        for record in result:
            print(f"Conference => {record['conference']['name']}, Paper => {record['paper']['title']}, Citations => {record['numOfCitations']}")