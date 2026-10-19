package io.github.gunasekar89.pipeline;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.assertj.MockMvcTester;

/**
 * Boots the full application context, so it catches wiring and configuration
 * errors that the web slice cannot, and checks the operational endpoints that
 * Kubernetes probes and Prometheus will depend on.
 */
@SpringBootTest(properties = "app.environment=integration")
@AutoConfigureMockMvc
class ApplicationIntegrationTest {

    @Autowired
    private MockMvcTester mvc;

    @Test
    void helloEndpointUsesExternalisedConfiguration() {
        assertThat(mvc.get().uri("/api/hello"))
                .hasStatusOk()
                .bodyJson()
                .extractingPath("$.environment")
                .isEqualTo("integration");
    }

    @Test
    void healthEndpointReportsUp() {
        assertThat(mvc.get().uri("/actuator/health"))
                .hasStatusOk()
                .bodyJson()
                .extractingPath("$.status")
                .isEqualTo("UP");
    }

    @Test
    void livenessAndReadinessProbesAreExposed() {
        assertThat(mvc.get().uri("/actuator/health/liveness")).hasStatusOk();
        assertThat(mvc.get().uri("/actuator/health/readiness")).hasStatusOk();
    }

    @Test
    void prometheusEndpointPublishesJvmAndHttpMetrics() {
        mvc.get().uri("/api/hello").exchange();

        assertThat(mvc.get().uri("/actuator/prometheus"))
                .hasStatusOk()
                .bodyText()
                .contains("jvm_memory_used_bytes")
                .contains("http_server_requests_seconds_count")
                .contains("application=\"enterprise-devops-app\"");
    }

    @Test
    void sensitiveActuatorEndpointsAreNotExposed() {
        assertThat(mvc.get().uri("/actuator/env")).hasStatus4xxClientError();
        assertThat(mvc.get().uri("/actuator/heapdump")).hasStatus4xxClientError();
    }
}
