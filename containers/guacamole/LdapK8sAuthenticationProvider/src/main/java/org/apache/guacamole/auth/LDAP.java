package org.apache.guacamole.auth;

import java.util.Hashtable;
import javax.naming.Context;
import javax.naming.NamingException;
import javax.naming.directory.DirContext;
import javax.naming.directory.InitialDirContext;
import javax.naming.ldap.LdapName;
import javax.naming.ldap.Rdn;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Simple abstraction on communicating with an LDAP server.
 */
public class LDAP {

    private static final Logger logger = LoggerFactory.getLogger(LDAP.class);

    /**
     * Authenticates a user against an LDAP server.
     * @param ldapHostname Url to the LDAP server including protocol and port.
     * @param userBaseDN User search base DN.
     * @param userField User id field name.
     * @param username Username to authenticate as.
     * @param password Password to authenticate with.
     * @return True if authentication succeeds, otherwise false.
     */
    public static boolean authenticate(String ldapHostname, String userBaseDN, String userField, String username, String password) {

        // Construct the user's DN using the base DN, bind pattern, and username
        String userDN;
        try {
            LdapName dn = new LdapName(userBaseDN);
            dn.add(dn.size(), new Rdn(userField, username));
            userDN = dn.toString();
            logger.debug("Attempting LDAP bind for user '{}' with DN '{}'", username, userDN);

        } catch (Exception e) {
            logger.warn("LDAP DN formatting failed for user '{}': {}", username, e.getMessage());
            return false;
        }

        // Perform LDAP bind (authentication) with user credentials
        Hashtable<String, String> env = new Hashtable<>();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
        env.put(Context.PROVIDER_URL, ldapHostname);
        env.put(Context.SECURITY_AUTHENTICATION, "simple");
        env.put(Context.SECURITY_PRINCIPAL, userDN);
        env.put(Context.SECURITY_CREDENTIALS, password);

        try {
            // If the bind succeeds the user was authenticated
            DirContext ldapContext = new InitialDirContext(env);
        } catch (NamingException e) {
            // Authentication failed (invalid credentials or LDAP error)
            logger.warn("LDAP authentication failed for user '{}': {}", username, e.getMessage());
            return false;
        }

        // Successful authentication!
        logger.info("LDAP authentication succeeded for user '{}'", username);
        return true;
    }
}