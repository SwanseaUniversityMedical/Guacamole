package org.apache.guacamole.auth;

import java.util.Map;

import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import org.apache.guacamole.GuacamoleException;
import org.apache.guacamole.environment.Environment;
import org.apache.guacamole.environment.LocalEnvironment;
import org.apache.guacamole.net.auth.Credentials;
import org.apache.guacamole.net.auth.simple.SimpleAuthenticationProvider;
import org.apache.guacamole.protocol.GuacamoleConfiguration;
import org.apache.guacamole.properties.GuacamoleProperty;
import org.apache.guacamole.properties.StringGuacamoleProperty;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Provides a custom authentication and authorization method which authenticates
 * against LDAP and authorizes using kubernetes Connection CRDs.
 */
public class LdapK8sAuthenticationProvider extends SimpleAuthenticationProvider {

    private static final Logger logger = LoggerFactory.getLogger(LdapK8sAuthenticationProvider.class);

    private static final GuacamoleProperty<String> LDAP_URL = new StringGuacamoleProperty() {
        @Override
        public String getName() { return "ldap-url"; }
    };

    private static final GuacamoleProperty<String> LDAP_USER_BASE_DN = new StringGuacamoleProperty() {
        @Override
        public String getName() { return "ldap-user-base-dn"; }
    };

    private static final GuacamoleProperty<String> LDAP_USER_FIELD = new StringGuacamoleProperty() {
        @Override
        public String getName() { return "ldap-user-field"; }
    };

    private static final GuacamoleProperty<String> K8S_NAMESPACE = new StringGuacamoleProperty() {
        @Override
        public String getName() { return "k8s-namespace"; }
    };

    @Override
    public String getIdentifier() {
        // Unique identifier for this authentication provider
        return "ldapk8s";
    }

    /**
     * Overrides to provide a custom authentication and authorization method which authenticates
     * against LDAP and authorizes using kubernetes Connection CRDs.
     * @param credentials Credentials class passed from Guacamole.
     * @return Map of authorized Guacamole configurations.
     * @throws GuacamoleException Rethrows all exceptions as GuacamoleExecption's.
     */
    @Override
    public Map<String, GuacamoleConfiguration> getAuthorizedConfigurations(Credentials credentials)
            throws GuacamoleException {

        try {
            // Load LDAP configuration from guacamole.properties
            Environment environment = LocalEnvironment.getInstance();
            String ldapUrl = environment.getRequiredProperty(LDAP_URL).trim();
            String userBaseDN = environment.getRequiredProperty(LDAP_USER_BASE_DN).trim();
            String userField = environment.getRequiredProperty(LDAP_USER_FIELD).trim();
            String k8sNamespace = environment.getRequiredProperty(K8S_NAMESPACE).trim();

            // Retrieve user credentials
            String username = credentials.getUsername();
            String password = credentials.getPassword();
            if (username == null || password == null || username.isEmpty() || password.isEmpty()) {
                // Missing credentials – do not authorize
                return null;
            }

            // Attempt to bind to LDAP using the users credentials
            if (!LDAP.authenticate(ldapUrl, userBaseDN, userField, username, password)) {
                return null;
            }

            // Attempt to retrieve the users set of Connections from the kube api
            try (final KubernetesClient client = new KubernetesClientBuilder().build()) {
                return K8s.authorize(client, k8sNamespace, username);
            }
        }
        catch (Exception e) {
            throw new GuacamoleException(e);
        }
    }
}
