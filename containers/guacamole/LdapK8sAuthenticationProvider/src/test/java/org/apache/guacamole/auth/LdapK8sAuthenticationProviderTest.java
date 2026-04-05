package org.apache.guacamole.auth;

import java.io.IOException;
import java.util.Map;

import java.nio.file.*;
import org.junit.jupiter.api.io.TempDir;

import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.server.mock.EnableKubernetesMockClient;

import org.apache.guacamole.net.RequestDetails;
import org.apache.guacamole.GuacamoleException;
import org.apache.guacamole.net.auth.Credentials;
import org.apache.guacamole.protocol.GuacamoleConfiguration;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@EnableKubernetesMockClient(crud=true)
class LdapK8sAuthenticationProviderTest {

    KubernetesClient client;

    @TempDir Path temp;

    @BeforeAll
    void setUpLdap() throws Exception {
        MockLDAP.start();
    }

    @BeforeEach
    void setUpK8s() throws IOException {
        MockK8s.start(client);
    }

    @AfterAll
    void tearDown() {
        MockLDAP.stop();
    }

    // TODO this test suite requires a way to get
    //  Environment environment = LocalEnvironment.getInstance();
    //  to load values from the environment when not running within Guacamole.
    //  It also requires a way to transparently initialize the k8s mock api.

//    @Test
//    @DisplayName("Authorize bob")
//    void authorize_bob() throws GuacamoleException {
//
//        Credentials credentials = new Credentials("bob", "secret", (RequestDetails) null);
//
//        Map<String, GuacamoleConfiguration> configs =
//                new LdapK8sAuthenticationProvider().getAuthorizedConfigurations(credentials);
//
//        assertEquals(2, configs.size(),
//                "Expected configs to have two connections for bob");
//
//        assertTrue(configs.containsKey("bob.0000.example.com"),
//                "Expected bob to have connection bob.0000.example.com");
//
//        assertTrue(configs.containsKey("bob.0001.example.com"),
//                "Expected bob to have connection bob.0001.example.com");
//
//    }
}