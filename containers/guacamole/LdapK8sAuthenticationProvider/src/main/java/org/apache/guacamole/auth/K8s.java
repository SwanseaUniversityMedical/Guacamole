package org.apache.guacamole.auth;

import org.apache.guacamole.protocol.GuacamoleConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;

import io.fabric8.kubernetes.api.model.KubernetesResourceList;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClientBuilder;
import io.fabric8.kubernetes.client.dsl.MixedOperation;
import io.fabric8.kubernetes.client.dsl.Resource;

/**
 * Simple abstraction on communicating with the kube api.
 */
public class K8s {

    private static final Logger logger = LoggerFactory.getLogger(K8s.class);

    /**
     * Authorizes a user against Connection CRDs in the kube api.
     * @param client Kubernetes client object initialized to the cluster.
     * @param k8sNamespace Namespace to search for Connection CRDs.
     * @param username Username to authorize.
     * @return Map of Guacamole configurations.
     */
    public static Map<String, GuacamoleConfiguration> authorize(KubernetesClient client, String k8sNamespace, String username) {

        Map<String, GuacamoleConfiguration> configs =
                new HashMap<String, GuacamoleConfiguration>();

        logger.debug("Listing Connections in namespace '{}'", k8sNamespace);

        // Get a client for the Connection custom resource
        MixedOperation<Connection, KubernetesResourceList<Connection>, Resource<Connection>> connClient
                = client.resources(Connection.class);

        // List all Connection resources in namespace
        KubernetesResourceList<Connection> connectionList = connClient.inNamespace(k8sNamespace).list();
        for (Connection conn : connectionList.getItems()) {

            Connection.ConnectionSpec spec = conn.getSpec();
            Connection.ConnectionStatus status = conn.getStatus();

            if (spec == null || status == null) {
                continue;
            }

            if (!username.equals(spec.getUsername())) {
                continue;
            }

            if (!spec.isEnabled()) {
                logger.debug("Skipping disabled Connection '{}' '{}'", username, conn.getFullResourceName());
                continue;
            }

            // Check if status.lastAuthorized is within the last 5 minutes
            long now = System.currentTimeMillis() / 1000;
            long threshold = now - (60 * 5);
            if (status.getLastAuthorized() < threshold) {
                logger.debug("Skipping stale Connection '{}' '{}'", username, conn.getFullResourceName());
                continue;
            }

            logger.info("Found Connection '{}' '{}'", username, conn.getFullResourceName());

            // Add a Guacamole connection to the result
            GuacamoleConfiguration config = new GuacamoleConfiguration();
            config.setProtocol("rdp");
            config.setParameter("hostname", spec.getHostname());
            config.setParameter("port", "3389");
            configs.put(spec.getHostname(), config);
        }

        return configs;
    }
}