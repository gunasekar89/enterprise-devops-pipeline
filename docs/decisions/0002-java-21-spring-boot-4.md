# ADR-0002: Java 21 with Spring Boot 4.1

- Status: Accepted
- Date: 2026-10-19

## Context

The project needs a small but realistic Java service on a currently maintained stack. Java 21 was already installed on `vm-jenkins-lab`. The brief asked for "a compatible maintained Spring Boot version".

## Options

1. **Spring Boot 3.5.x** (latest 3.x: 3.5.16). Most tutorials and interview material still use 3.x. However, according to the Spring Boot support calendar, open-source support for 3.5 ended in mid-2026; further fixes require commercial support. *Verify at <https://spring.io/projects/spring-boot#support> when revisiting.*
2. **Spring Boot 4.1.x** (4.1.1, the newest release on Maven Central on 2026-10-19). Supported Java baseline 17, works on 21. Built on Spring Framework 7 and Jackson 3.
3. **Spring Boot 4.0.x**, older 4.x line with a shorter remaining support window.

## Decision

Spring Boot 4.1.1 on Java 21, built with Maven 3.9.11 through the Maven wrapper.

## Consequences

- The stack receives open-source security fixes for the life of this project's next phases.
- Some names differ from 3.x material: the web starter is `spring-boot-starter-webmvc`, the web test slice needs `spring-boot-starter-webmvc-test`, and `@WebMvcTest` lives in `org.springframework.boot.webmvc.test.autoconfigure`. JSON uses Jackson 3 (`tools.jackson` packages).
- Tests use `MockMvcTester` (AssertJ style), the current recommended API.
- Maven Enforcer rejects JDKs older than 21 and Maven older than 3.9, so a wrong agent fails fast.
- Even the newest Boot release shipped with vulnerable Tomcat and Jackson versions (see known issues #8). Managed-version overrides are allowed, documented in the POM and removed on the next Boot upgrade.
