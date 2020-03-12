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

