package loader;

import java.sql.Connection;

public class Neo4JLoader
{
    // PRIVATE CLASS MEMBERS
    private static final String RESOURCES_PATH = "src/main/resources";
    private Connection connection;

    /**
     * Neo4JLoader constructor
     *
     * @param connection to the neo4j database
     */
    public Neo4JLoader(Connection connection)
    {
        this.connection = connection;
    }

    public void loadJournalPapers()
    {

    }
}
