package org.apache.guacamole.auth;

import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.server.mock.EnableKubernetesMockClient;

import java.util.Map;
import org.apache.guacamole.protocol.GuacamoleConfiguration;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@EnableKubernetesMockClient(crud=true)
class K8sTest {

    KubernetesClient client;

    @BeforeEach
    void setUp() {
        MockK8s.start(client);
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