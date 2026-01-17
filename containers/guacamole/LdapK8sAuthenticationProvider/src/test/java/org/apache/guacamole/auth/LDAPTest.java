package org.apache.guacamole.auth;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

import javax.naming.InvalidNameException;
import javax.naming.ldap.LdapName;
import javax.naming.ldap.Rdn;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class LDAPTest {

    private final String ldapUrl = "ldap://127.0.0.1:389";
    private final String userBaseDN = "ou=people,dc=example,dc=org";
    private final String userBindField = "uid";

    @Test
    @DisplayName("Authenticates bob with good password")
    void authenticate_bob_good() throws InvalidNameException {

        assertTrue(LDAP.authenticate(
                ldapUrl,
                userBaseDN,
                userBindField,
                "bob",
                "secret"
        ), "Expected LDAP authentication to succeed for bob with good password");
    }

    @Test
    @DisplayName("Authenticates bob with bad password")
    void authenticate_bob_bad() {
        assertFalse(LDAP.authenticate(
                ldapUrl,
                userBaseDN,
                userBindField,
                "bob",
                "squirrel"
        ), "Expected LDAP authentication to fail for bob with bad password");
    }

    @Test
    @DisplayName("Authenticates alice with good password")
    void authenticate_alice_good() {
        assertTrue(LDAP.authenticate(
                ldapUrl,
                userBaseDN,
                userBindField,
                "alice",
                "squirrel"
        ), "Expected LDAP authentication to succeed for alice with good password");
    }

    @Test
    @DisplayName("Authenticates alice with bad password")
    void authenticate_alice_bad() {
        assertFalse(LDAP.authenticate(
                ldapUrl,
                userBaseDN,
                userBindField,
                "alice",
                "secret"
        ), "Expected LDAP authentication to fail for alice with bad password");
    }

    @Test
    @DisplayName("Authenticates eve with bad password")
    void authenticate_eve_bad() {
        assertFalse(LDAP.authenticate(
                ldapUrl,
                userBaseDN,
                userBindField,
                "eve",
                "buffalo"
        ), "Expected LDAP authentication to fail for eve with bad password");
    }
}
