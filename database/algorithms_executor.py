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
        session = self._driver.session()
        communities = set()
        dictionary = dict()
        results = session.run("""
                    CALL algo.beta.louvain.stream('ScientificPaper', 'CITES', {
                    graph: 'huge',
                    direction: 'BOTH',
                    includeIntermediateCommunities: true
                    }) YIELD nodeId, community, communities
                    RETURN algo.asNode(nodeId).title as title, community
                    ORDER BY community ASC
                     """)
        for item in results:
            key = item['community']
            value = item['title']
            print("[%s, %s]" % (key, value))
            communities.add(key)
            if key in dictionary:
                dictionary[key] += 1
            else:
                dictionary[key] = 1
        print("Community Clusters %s" % dictionary)
        return dictionary

    def run_page_rank_algorithm(self):
        session = self._driver.session()
        scores = []
        results = session.run("""
                        CALL algo.pageRank.stream('ScientificPaper', 'CITES', {
                        iterations:20
                        })
                        YIELD nodeId, score
                        RETURN algo.asNode(nodeId).title  AS paper,score
                        ORDER BY score DESC LIMIT 10
                            """)
        print("Paper, Score")
        for item in results:
            paper = item['paper']
            score = item['score']
            print("[%s, %s]" % (paper, score))
            scores.append((paper, score))
        return scores


