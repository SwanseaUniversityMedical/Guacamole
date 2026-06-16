package org.apache.guacamole.auth;

import io.fabric8.kubernetes.api.model.Namespaced;
import io.fabric8.kubernetes.client.CustomResource;
import io.fabric8.kubernetes.model.annotation.Group;
import io.fabric8.kubernetes.model.annotation.Version;
import io.fabric8.kubernetes.model.annotation.Plural;

/**
 * Java digital twin of the Connection CRD.
 */
@Group("serp-lite.serp.uk")
@Version("v1")
@Plural("connections")
public class Connection extends CustomResource<Connection.ConnectionSpec, Connection.ConnectionStatus> implements Namespaced {
    // Spec sub-class
    public static class ConnectionSpec {
        private String username;
        private String hostname;
        private boolean enabled;

        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }

        public String getHostname() { return hostname; }
        public void setHostname(String hostname) { this.hostname = hostname; }

        public boolean isEnabled() { return enabled; }
        public void setEnabled(boolean enabled) { this.enabled = enabled; }
    }
    // Status sub-class
    public static class ConnectionStatus {
        private long lastAuthorized;
        public long getLastAuthorized() { return lastAuthorized; }
        public void setLastAuthorized(long lastAuthorized) { this.lastAuthorized = lastAuthorized; }
    }
}