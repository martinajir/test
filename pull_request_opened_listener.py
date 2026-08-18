#!/usr/bin/env python3
"""Receive GitHub webhook deliveries for opened pull requests."""

import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit


LOGGER = logging.getLogger("pull_request_opened_listener")
MAX_PAYLOAD_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True)
class WebhookResponse:
    status: int
    result: str
    message: str

    def as_json(self) -> bytes:
        return json.dumps(
            {"result": self.result, "message": self.message},
            separators=(",", ":"),
        ).encode("utf-8")


def verify_signature(body: bytes, secret: str, signature: str | None) -> bool:
    """Validate a delivery using GitHub's X-Hub-Signature-256 scheme."""
    if not signature:
        return False

    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={digest}", signature)


def handle_webhook(
    body: bytes,
    event: str | None,
    signature: str | None,
    secret: str,
) -> WebhookResponse:
    """Validate and classify one GitHub webhook delivery."""
    if not verify_signature(body, secret, signature):
        return WebhookResponse(403, "rejected", "Invalid webhook signature")

    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return WebhookResponse(400, "rejected", "Request body is not valid JSON")

    if not isinstance(payload, dict):
        return WebhookResponse(400, "rejected", "Webhook payload must be an object")

    if not event:
        return WebhookResponse(400, "rejected", "X-GitHub-Event header is missing")

    if event == "ping":
        return WebhookResponse(202, "accepted", "GitHub ping received")

    if event != "pull_request":
        return WebhookResponse(202, "ignored", f"Ignored {event} event")

    action = payload.get("action")
    if action != "opened":
        return WebhookResponse(
            202,
            "ignored",
            f"Ignored pull_request action: {action or 'missing'}",
        )

    try:
        repository = payload["repository"]["full_name"]
        pull_request = payload["pull_request"]
        number = pull_request["number"]
        title = pull_request["title"]
        url = pull_request["html_url"]
        sender = payload["sender"]["login"]
    except (KeyError, TypeError):
        return WebhookResponse(
            400,
            "rejected",
            "Opened pull request payload is missing required fields",
        )

    fields: tuple[tuple[Any, type], ...] = (
        (repository, str),
        (number, int),
        (title, str),
        (url, str),
        (sender, str),
    )
    if any(type(value) is not expected for value, expected in fields):
        return WebhookResponse(
            400,
            "rejected",
            "Opened pull request payload has invalid field types",
        )

    message = (
        f"Pull request #{number} opened in {repository} by {sender}: "
        f"{title} ({url})"
    )
    return WebhookResponse(202, "processed", message)


class PullRequestWebhookHandler(BaseHTTPRequestHandler):
    """HTTP adapter for the webhook handling logic."""

    webhook_secret = ""

    def do_GET(self) -> None:
        if urlsplit(self.path).path != "/health":
            self._send(WebhookResponse(404, "rejected", "Not found"))
            return
        self._send(WebhookResponse(200, "ok", "Listener is ready"))

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/webhook":
            self._send(WebhookResponse(404, "rejected", "Not found"))
            return

        content_length = self.headers.get("Content-Length")
        if content_length is None:
            self._send(
                WebhookResponse(411, "rejected", "Content-Length header is required")
            )
            return

        try:
            length = int(content_length)
        except ValueError:
            self._send(
                WebhookResponse(400, "rejected", "Content-Length header is invalid")
            )
            return

        if length < 0:
            self._send(
                WebhookResponse(400, "rejected", "Content-Length header is invalid")
            )
            return
        if length > MAX_PAYLOAD_BYTES:
            self._send(WebhookResponse(413, "rejected", "Webhook payload is too large"))
            return

        body = self.rfile.read(length)
        response = handle_webhook(
            body=body,
            event=self.headers.get("X-GitHub-Event"),
            signature=self.headers.get("X-Hub-Signature-256"),
            secret=self.webhook_secret,
        )
        if response.result == "processed":
            LOGGER.info(response.message)
        self._send(response)

    def _send(self, response: WebhookResponse) -> None:
        body = response.as_json()
        self.send_response(response.status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, message_format: str, *args: Any) -> None:
        LOGGER.info("%s - %s", self.address_string(), message_format % args)


def make_handler(secret: str) -> type[PullRequestWebhookHandler]:
    """Create a handler class configured with a webhook secret."""

    class ConfiguredHandler(PullRequestWebhookHandler):
        pass

    ConfiguredHandler.webhook_secret = secret
    return ConfiguredHandler


def main() -> None:
    secret = os.environ.get("WEBHOOK_SECRET")
    if not secret:
        raise SystemExit("WEBHOOK_SECRET must be set")

    host = os.environ.get("HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("PORT", "3000"))
    except ValueError as error:
        raise SystemExit("PORT must be an integer") from error
    if not 1 <= port <= 65535:
        raise SystemExit("PORT must be between 1 and 65535")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    server = ThreadingHTTPServer((host, port), make_handler(secret))
    LOGGER.info("Listening on http://%s:%s/webhook", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOGGER.info("Stopping listener")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
