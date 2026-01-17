ARG GUAC_VERSION=1.5.0
FROM maven:3.9-eclipse-temurin-11 AS build

WORKDIR /build
COPY LdapK8sAuthenticationProvider/pom.xml ./
RUN mvn -q -DskipTests dependency:go-offline
COPY LdapK8sAuthenticationProvider/src ./src
RUN mvn -q -DskipTests package \
 && mvn -q -DskipTests dependency:copy-dependencies \
      -DincludeScope=runtime \
      -DoutputDirectory=target/dependency


FROM guacamole/guacamole:${GUAC_VERSION}

# The official image uses /etc/guacamole as GUACAMOLE_HOME by default
# Extensions must go in: /etc/guacamole/extensions
# Optional libs go in: /etc/guacamole/lib
USER root
RUN mkdir -p /etc/guacamole/extensions /etc/guacamole/lib

COPY --from=build /build/target/*.jar /etc/guacamole/extensions/
#COPY --from=build /build/target/dependency/*.jar /etc/guacamole/lib/

USER 0
