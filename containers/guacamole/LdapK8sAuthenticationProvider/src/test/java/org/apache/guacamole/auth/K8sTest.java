package org.apache.guacamole.auth;

import io.fabric8.kubernetes.api.model.KubernetesResourceList;
import io.fabric8.kubernetes.api.model.ObjectMetaBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;
import io.fabric8.kubernetes.client.server.mock.EnableKubernetesMockClient;
import org.apache.guacamole.protocol.GuacamoleConfiguration;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@EnableKubernetesMockClient(crud=true)
class K8sTest {

    static Connection createConnection(String name, String username, String hostname, boolean enabled, long age) {

        Connection connection = new Connection();
        connection.setMetadata(new ObjectMetaBuilder().withName(name).build());

        Connection.ConnectionSpec connectionSpec = new Connection.ConnectionSpec();
        connectionSpec.setUsername(username);
        connectionSpec.setHostname(hostname);
        connectionSpec.setEnabled(enabled);
        connection.setSpec(connectionSpec);

        Connection.ConnectionStatus connectionStatus = new Connection.ConnectionStatus();
        connectionStatus.setLastAuthorized((System.currentTimeMillis() / 1000) - age);
        connection.setStatus(connectionStatus);

        return connection;
    }

    KubernetesClient client;

    @BeforeEach
    void setUp() {

        client.getKubernetesSerialization().registerKubernetesResource("serp-lite.serp.uk/v1", "Connection", Connection.class);

        MixedOperation<Connection, KubernetesResourceList<Connection>, Resource<Connection>> connectionClient =
                client.resources(Connection.class);

        connectionClient.inNamespace("guacamole-ldap-k8s-auth-test").create(createConnection(
            "bob-0000",
            "bob",
            "bob.0000.example.com",
            true,
            0
        ));

        connectionClient.inNamespace("guacamole-ldap-k8s-auth-test").create(createConnection(
                "bob-0001",
                "bob",
                "bob.0001.example.com",
                true,
                0
        ));

        connectionClient.inNamespace("guacamole-ldap-k8s-auth-test").create(createConnection(
                "alice-0000",
                "alice",
                "alice.0000.example.com",
                true,
                0
        ));

        connectionClient.inNamespace("guacamole-ldap-k8s-auth-test").create(createConnection(
                "alice-0001",
                "alice",
                "alice.0001.example.com",
                false,
                0
        ));

        connectionClient.inNamespace("guacamole-ldap-k8s-auth-test").create(createConnection(
                "alice-0002",
                "alice",
                "alice.0002.example.com",
                true,
                60 * 6
        ));

    }

    @Test
    @DisplayName("Authorize bob")
    void authorize_bob() {

        Map<String, GuacamoleConfiguration> configs =
                K8s.authorize(client, "guacamole-ldap-k8s-auth-test", "bob");

        assertEquals(2, configs.size(),
                "Expected configs to have two connections for bob");

        assertTrue(configs.containsKey("bob.0000.example.com"),
                "Expected bob to have connection bob.0000.example.com");

        assertTrue(configs.containsKey("bob.0001.example.com"),
                "Expected bob to have connection bob.0001.example.com");

    }

    @Test
    @DisplayName("Authorize alice")
    void authorize_alice() {

        Map<String, GuacamoleConfiguration> configs =
                K8s.authorize(client, "guacamole-ldap-k8s-auth-test", "alice");

        assertEquals(1, configs.size(),
                "Expected configs to have one connection for alice");

        assertTrue(configs.containsKey("alice.0000.example.com"),
                "Expected alice to have connection alice.0000.example.com");

    }

    @Test
    @DisplayName("Authorize eve")
    void authorize_eve() {

        Map<String, GuacamoleConfiguration> configs =
                K8s.authorize(client,"guacamole-ldap-k8s-auth-test", "eve");

        assertEquals(0, configs.size(),
                "Expected configs to have zero connections for eve");

    }
}