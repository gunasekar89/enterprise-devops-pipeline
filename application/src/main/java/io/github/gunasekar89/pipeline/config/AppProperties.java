package io.github.gunasekar89.pipeline.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;

/**
 * Application settings bound from the {@code app.*} namespace.
 * Every value can be overridden with an environment variable, e.g.
 * {@code APP_GREETING=Hi} or {@code APP_ENVIRONMENT=dev}.
 */
@ConfigurationProperties(prefix = "app")
public record AppProperties(
        @DefaultValue("Hello") String greeting,
        @DefaultValue("local") String environment) {
}
