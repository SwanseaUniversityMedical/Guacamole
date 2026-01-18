package org.apache.guacamole.auth;

import io.fabric8.kubernetes.api.model.KubernetesResourceList;
import io.fabric8.kubernetes.api.model.ObjectMetaBuilder;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;

public class MockK8s {

    private static Connection createConnection(String name, String username, String hostname, boolean enabled, long age) {

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

    public static void start(KubernetesClient client) {

        client.getKubernetesSerialization()
                .registerKubernetesResource("serp-lite.serp.uk/v1", "Connection", Connection.class);

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
}
