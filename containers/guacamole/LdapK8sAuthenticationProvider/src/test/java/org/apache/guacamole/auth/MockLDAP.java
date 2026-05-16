package org.apache.guacamole.auth;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;

import java.net.InetAddress;

public class MockLDAP {

    public static final String ldapHostname = "ldap://127.0.0.1:389";
    public static final String userBaseDN = "ou=people,dc=example,dc=org";
    public static final String userField = "uid";
    private static InMemoryDirectoryServer server;

    public static void start() throws Exception {

        InMemoryDirectoryServerConfig config =
                new InMemoryDirectoryServerConfig("dc=example,dc=org");

        config.setListenerConfigs(
                InMemoryListenerConfig.createLDAPConfig(
                        "default",
                        InetAddress.getByName("127.0.0.1"),
                        389,
                        null
                )
        );

        server = new InMemoryDirectoryServer(config);
        server.startListening();

        // Prepopulate directory
        server.importFromLDIF(true, "src/test/resources/test.ldif");
    }

    public static void stop() {
        if (server != null) server.shutDown(true);
    }
}
