package com.example.webserver;

import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

/**
 * A minimal Java web server using the JDK's built-in HttpServer (no external
 * dependencies required). Listens on the port given by the PORT environment
 * variable, defaulting to 8080.
 */
public class App {

    public static void main(String[] args) throws IOException {
        int port = getPort();

        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/", exchange -> {
            String response = "Hello, world! This is a simple Java web server.\n";
            exchange.getResponseHeaders().add("Content-Type", "text/plain; charset=utf-8");
            exchange.sendResponseHeaders(200, response.getBytes(StandardCharsets.UTF_8).length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes(StandardCharsets.UTF_8));
            }
        });

        server.createContext("/health", exchange -> {
            String response = "OK\n";
            exchange.sendResponseHeaders(200, response.getBytes(StandardCharsets.UTF_8).length);
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes(StandardCharsets.UTF_8));
            }
        });

        server.setExecutor(null); // default executor
        server.start();

        System.out.println("Server started on port " + port);
    }

    private static int getPort() {
        String portEnv = System.getenv("PORT");
        if (portEnv != null && !portEnv.isBlank()) {
            try {
                return Integer.parseInt(portEnv.trim());
            } catch (NumberFormatException e) {
                System.err.println("Invalid PORT value '" + portEnv + "', falling back to 8080");
            }
        }
        return 8080;
    }
}
