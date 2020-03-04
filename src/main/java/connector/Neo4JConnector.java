package connector;

import java.sql.Connection;
import java.sql.SQLException;
import java.sql.DriverManager;

public class Neo4JConnector
{

    /**
     * Connect to the database
     *
     * @param user database user
     * @param password database password
     * @return Connection | null
     */
    public Connection connect(String user, String password)
    {
        try {
            Connection connection = DriverManager.getConnection("jdbc:neo4j:http://localhost", user, password);
            return connection;
        }
        catch (SQLException exception) {
            exception.printStackTrace();
        }

        return null;
    }

}
