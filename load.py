from database.neo4j_loader import Neo4JLoader

if __name__ == "__main__":
    neo4j = Neo4JLoader()
    neo4j.load()
    # neo4j.evolve() # uncomment if you want to evolve the graph

