package org.apache.guacamole.auth;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;

import javax.naming.InvalidNameException;

import static org.junit.jupiter.api.Assertions.*;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class LDAPTest {

    @BeforeAll
    void setUp() throws Exception {
        MockLDAP.start();
    }

    @AfterAll
    void tearDown() {
        MockLDAP.stop();
    }

    @Test
    @DisplayName("Authenticates bob with good password")
    void authenticate_bob_good() throws InvalidNameException {

        assertTrue(LDAP.authenticate(
                MockLDAP.ldapHostname,
                MockLDAP.userBaseDN,
                MockLDAP.userField,
                "bob",
                "secret"
        ), "Expected LDAP authentication to succeed for bob with good password");
    }

    @Test
    @DisplayName("Authenticates bob with bad password")
    void authenticate_bob_bad() {
        assertFalse(LDAP.authenticate(
                MockLDAP.ldapHostname,
                MockLDAP.userBaseDN,
                MockLDAP.userField,
                "bob",
                "squirrel"
        ), "Expected LDAP authentication to fail for bob with bad password");
    }

    @Test
    @DisplayName("Authenticates alice with good password")
    void authenticate_alice_good() {
        assertTrue(LDAP.authenticate(
                MockLDAP.ldapHostname,
                MockLDAP.userBaseDN,
                MockLDAP.userField,
                "alice",
                "squirrel"
        ), "Expected LDAP authentication to succeed for alice with good password");
    }

    @Test
    @DisplayName("Authenticates alice with bad password")
    void authenticate_alice_bad() {
        assertFalse(LDAP.authenticate(
                MockLDAP.ldapHostname,
                MockLDAP.userBaseDN,
                MockLDAP.userField,
                "alice",
                "secret"
        ), "Expected LDAP authentication to fail for alice with bad password");
    }

    @Test
    @DisplayName("Authenticates eve with bad password")
    void authenticate_eve_bad() {
        assertFalse(LDAP.authenticate(
                MockLDAP.ldapHostname,
                MockLDAP.userBaseDN,
                MockLDAP.userField,
                "eve",
                "buffalo"
        ), "Expected LDAP authentication to fail for eve with bad password");
    }
}
