import os

from neo4j import GraphDatabase


class AlgorithmsExecutor(object):

    def __init__(self):
        """
        Neo4jLoader constructor
        """
        uri = "bolt://localhost:7687"
        self._driver = GraphDatabase.driver(uri, auth=('neo4j', 'karim'), encrypted=False)
        # self._driver = GraphDatabase.driver(os.getenv('DB_URI'),
        #                                     auth=(os.getenv('DB_USER'), os.getenv('DB_PASSWORD')), encrypted=False)

    def run_louvain_algorithm(self):
        print("\nRUNNING LOUVAIN....")
        session = self._driver.session()
        dictionary = dict()
        results = session.run("""
                    CALL algo.beta.louvain.stream('ScientificPaper', 'CITES', {
                    graph: 'huge',
                    direction: 'BOTH'
                    }) 
                    YIELD nodeId, community
                    MATCH (n:ScientificPaper) WHERE id(n)=nodeId
                    RETURN community,
                    count(*) as communitySize, 
                    collect(n.title) as members 
                    order by communitySize desc limit 5
                     """)
        for item in results:
             print("\nCommunity Number %s   Community Size  %s   Community Members: \n" % (item['community'], item['communitySize']))
             print (item['members'])

        return dictionary

    def run_page_rank_algorithm(self):
        print("RUNNING PAGERANK....")
        session = self._driver.session()
        scores = []
        results = session.run("""
                        CALL algo.pageRank.stream('ScientificPaper', 'CITES', {
                        iterations:20,
                        direction:'INCOMING'
                        })
                        YIELD nodeId, score
                        RETURN algo.asNode(nodeId).title  AS scientificPaper,score
                        ORDER BY score DESC LIMIT 10
                            """)
        print("[Paper, \t\t\t\t\tScore]")
        for item in results:
            paper = item['scientificPaper']
            score = item['score']
            print("[%s, %s]" % (paper, score))
            scores.append((paper, score))
        return scores


