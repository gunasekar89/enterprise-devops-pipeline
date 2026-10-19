package io.github.gunasekar89.pipeline.api;

import io.github.gunasekar89.pipeline.config.AppProperties;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HelloController {

    static final int MAX_NAME_LENGTH = 64;

    private final AppProperties properties;

    public HelloController(AppProperties properties) {
        this.properties = properties;
    }

    @GetMapping("/hello")
    public HelloResponse hello(@RequestParam(defaultValue = "World") String name) {
        return new HelloResponse(
                "%s, %s!".formatted(properties.greeting(), sanitize(name)),
                properties.environment());
    }

    /** Trims, bounds and strips control characters so user input cannot forge log lines or bloat responses. */
    static String sanitize(String name) {
        String cleaned = name.strip().replaceAll("\\p{Cntrl}", "");
        if (cleaned.isEmpty()) {
            return "World";
        }
        return cleaned.length() > MAX_NAME_LENGTH ? cleaned.substring(0, MAX_NAME_LENGTH) : cleaned;
    }

    public record HelloResponse(String message, String environment) {
    }
}
