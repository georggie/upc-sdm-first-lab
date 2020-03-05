from database.neo4j_loader import Neo4JLoader
import os
import settings

test = Neo4JLoader()
test._load_journals()