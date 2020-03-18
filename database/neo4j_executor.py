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

    def conference_community(self):
        """
        Finds community of each conference
        :return:
        """
        session = self._driver.session()

        result = session.run("""
                MATCH (author:Author)--(scientificPaper:ScientificPaper)-[:IS_IN]->(:Proceeding)-[:OF_A]->(conference:Conference),(conference)-[:HAS]->(edition:Edition)
                WITH author, conference, count(edition) as appearance
                ORDER BY appearance DESC
                WHERE appearance > 4
                RETURN author, conference, appearance
            """)

        for record in result:
            print(f"Author => {record['author']['name']}, Conference => {record['conference']['name']}, Appearance => {record['appearance']}")

    def journal_impact_factor(self):
        """
        Finds journal impact factor
        :return:
        """
        session = self._driver.session()

        result = session.run("""
                MATCH (scientificPaper:ScientificPaper)-[:PUBLISHED_IN]->(journal:Journal)-[:BELONGS_TO]->(:Volume)-[:ISSUED]->(year:Year), (scientificPaper)<-[:CITES]-(citingPaper:ScientificPaper)
                WHERE year.year = "2018.0" OR year.year = "2019.0"
                WITH scientificPaper, journal, COUNT(citingPaper) as citations
                WITH count(scientificPaper) as totalPublications, journal, sum(citations) as totalCitations
                RETURN journal, toFloat(totalCitations / totalPublications) as impactfactor
            """)

        for record in result:
            print(f"Journal => {record['journal']['name']}, ImpactFactor => {record['impactfactor']}")

    def recommend(self):
        """
        Recommend authors for paper review
        :return:
        """

        session = self._driver.session()

        session.run("""
                MATCH (sp:ScientificPaper)-[:MENTIONES]->(keyw:Keyword)
                WHERE keyw.name = "data management" or keyw.name = "indexing" or keyw.name = "data modeling" or keyw.name = "big data" or keyw.name = "data processing" or keyw.name = "data storage" or keyw.name = "data querying"
                SET sp.topic = "Databases"
            """)

        session.run("""
            call apoc.cypher.run('
            MATCH (scientificPaper:ScientificPaper)-[:IS_IN]->(proceeding:Proceeding)
            WITH proceeding, COUNT(DISTINCT scientificPaper) AS totalPapers
            MATCH (scientificPaper:ScientificPaper {topic: "Databases"})-[:IS_IN]->(proceeding)
            WITH proceeding, totalPapers, COUNT(DISTINCT scientificPaper) as databasePapers
            WHERE toFloat(databasePapers) / totalPapers > 0.9
            RETURN proceeding AS JournalWorkshopConference
            UNION
            MATCH (scientificPaper:ScientificPaper)-[:PUBLISHED_IN]->(journal:Journal)
            WITH journal, COUNT(DISTINCT scientificPaper) AS totalPapers
            MATCH (scientificPaper:ScientificPaper {topic: "Databases"})-[:PUBLISHED_IN]->(journal)
            WITH journal, totalPapers, COUNT(DISTINCT scientificPaper) as databasePapers
            WHERE toFloat(databasePapers) / totalPapers > 0.9
            RETURN journal AS JournalWorkshopConference', {}) yield value
            WITH value.JournalWorkshopConference as jwc
            MATCH (sp:ScientificPaper)--(jwc)
            WITH DISTINCT jwc
            SET jwc.community = "Database"
        """)

        session.run("""
            CALL algo.pageRank.stream('ScientificPaper', 'CITES', {iterations:20})
            YIELD nodeId, score
            CALL apoc.cypher.run('
            MATCH (scientificPaper:ScientificPaper {topic: "Databases"})-[:IS_IN]->(proceeding:Proceeding {community:"Database"})
            RETURN scientificPaper, proceeding as jwc
            UNION
            MATCH (scientificPaper:ScientificPaper {topic: "Databases"})-[:PUBLISHED_IN]->(journal:Journal {community: "Database"})
            RETURN scientificPaper, journal as jwc', {}) yield value
            WITH value.scientificPaper as paper, value.jwc as jwc, score
            WHERE id(paper) = nodeId
            WITH paper, jwc, score
            LIMIT 100
            SET paper.Top100 = True
        """)

        result = session.run("""
            MATCH (author:Author)-[:IS_LEAD_AUTHOR|:IS_CO_AUTHOR]->(sp:ScientificPaper {Top100: True})
            WITH author, COUNT(sp) as total
            WHERE total >=2
            RETURN author
            UNION
            MATCH (author:Author)-[:IS_LEAD_AUTHOR|:IS_CO_AUTHOR]->(sp:ScientificPaper {Top100: True})
            RETURN DISTINCT author
        """)

        for record in result:
            print(f"Author => {record['author']['name']}")



