import connector.Neo4JConnector;

import java.sql.Connection;

public class Main
{
    public static void main(String[] args)
    {
        // get an instance of the connector
        Neo4JConnector neo4JConnector = new Neo4JConnector();
        Connection connection = neo4JConnector.connect("neo4j", "juvebogdan32");


    }
}
