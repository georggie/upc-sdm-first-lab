import connector.Neo4JConnector;
import loader.Neo4JLoader;

import java.sql.Connection;

public class Main
{
    public static void main(String[] args)
    {
        // get an instance of the connector
        Neo4JConnector neo4JConnector = new Neo4JConnector();
        Connection connection = neo4JConnector.connect("neo4j", "juvebogdan32");

        // make an instance of the loader
        Neo4JLoader neo4JLoader = new Neo4JLoader(connection);
        neo4JLoader.loadJournalPapers();
    }
}
