package io.github.gunasekar89.pipeline.api;

import static org.assertj.core.api.Assertions.assertThat;

import io.github.gunasekar89.pipeline.config.AppProperties;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.assertj.MockMvcTester;

/** Web-layer slice: exercises request mapping, parameter binding and JSON serialisation only. */
@WebMvcTest(HelloController.class)
@EnableConfigurationProperties(AppProperties.class)
@TestPropertySource(properties = {"app.greeting=Hi", "app.environment=ci"})
class HelloControllerWebTest {

    @Autowired
    private MockMvcTester mvc;

    @Test
    void returnsDefaultGreetingAsJson() {
        assertThat(mvc.get().uri("/api/hello"))
                .hasStatus(HttpStatus.OK)
                .hasContentTypeCompatibleWith(MediaType.APPLICATION_JSON)
                .bodyJson()
                .isLenientlyEqualTo("""
                        {"message": "Hi, World!", "environment": "ci"}
                        """);
    }

    @Test
    void greetsTheRequestedName() {
        assertThat(mvc.get().uri("/api/hello").param("name", "Guna"))
                .hasStatusOk()
                .bodyJson()
                .extractingPath("$.message")
                .isEqualTo("Hi, Guna!");
    }

    @Test
    void unknownPathReturns404() {
        assertThat(mvc.get().uri("/api/does-not-exist")).hasStatus(HttpStatus.NOT_FOUND);
    }
}
