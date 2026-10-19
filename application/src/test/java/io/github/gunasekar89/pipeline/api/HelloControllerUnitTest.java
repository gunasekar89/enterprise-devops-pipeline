package io.github.gunasekar89.pipeline.api;

import static org.assertj.core.api.Assertions.assertThat;

import io.github.gunasekar89.pipeline.config.AppProperties;
import org.junit.jupiter.api.Test;

/** Plain unit tests: no Spring context, millisecond feedback. */
class HelloControllerUnitTest {

    private final HelloController controller = new HelloController(new AppProperties("Hello", "test"));

    @Test
    void buildsGreetingFromConfiguredPrefix() {
        assertThat(controller.hello("Guna").message()).isEqualTo("Hello, Guna!");
        assertThat(controller.hello("Guna").environment()).isEqualTo("test");
    }

    @Test
    void blankNameFallsBackToWorld() {
        assertThat(HelloController.sanitize("   ")).isEqualTo("World");
    }

    @Test
    void stripsControlCharactersToPreventLogForging() {
        assertThat(HelloController.sanitize("bob\r\nINFO fake entry")).isEqualTo("bobINFO fake entry");
    }

    @Test
    void truncatesOverlongNames() {
        assertThat(HelloController.sanitize("x".repeat(500))).hasSize(HelloController.MAX_NAME_LENGTH);
    }
}
