import hashlib
import hmac
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from pull_request_opened_listener import (
    handle_webhook,
    make_handler,
    verify_signature,
)


SECRET = "test-webhook-secret"


def encode(payload):
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def sign(body, secret=SECRET):
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def opened_payload():
    return {
        "action": "opened",
        "repository": {"full_name": "octocat/Hello-World"},
        "pull_request": {
            "number": 42,
            "title": "Improve the greeting",
            "html_url": "https://github.com/octocat/Hello-World/pull/42",
        },
        "sender": {"login": "monalisa"},
    }


class SignatureTests(unittest.TestCase):
    def test_matches_github_documentation_vector(self):
        body = b"Hello, World!"
        signature = (
            "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8"
            "b043e17"
        )

        self.assertTrue(
            verify_signature(body, "It's a Secret to Everybody", signature)
        )

    def test_rejects_missing_or_incorrect_signature(self):
        self.assertFalse(verify_signature(b"body", SECRET, None))
        self.assertFalse(verify_signature(b"body", SECRET, "sha256=incorrect"))


class WebhookTests(unittest.TestCase):
    def deliver(self, payload, event="pull_request"):
        body = encode(payload)
        return handle_webhook(body, event, sign(body), SECRET)

    def test_processes_opened_pull_request(self):
        response = self.deliver(opened_payload())

        self.assertEqual(202, response.status)
        self.assertEqual("processed", response.result)
        self.assertEqual(
            "Pull request #42 opened in octocat/Hello-World by monalisa: "
            "Improve the greeting "
            "(https://github.com/octocat/Hello-World/pull/42)",
            response.message,
        )

    def test_ignores_other_actions_and_events(self):
        closed = opened_payload()
        closed["action"] = "closed"

        self.assertEqual("ignored", self.deliver(closed).result)
        self.assertEqual(
            "ignored",
            self.deliver(opened_payload(), event="issues").result,
        )

    def test_accepts_ping(self):
        response = self.deliver({"zen": "Keep it logically awesome."}, event="ping")

        self.assertEqual(202, response.status)
        self.assertEqual("accepted", response.result)

    def test_rejects_bad_signature_before_parsing(self):
        response = handle_webhook(b"not json", "pull_request", "sha256=bad", SECRET)

        self.assertEqual(403, response.status)
        self.assertEqual("rejected", response.result)

    def test_rejects_invalid_json(self):
        body = b"not json"
        response = handle_webhook(body, "pull_request", sign(body), SECRET)

        self.assertEqual(400, response.status)
        self.assertEqual("Request body is not valid JSON", response.message)

    def test_rejects_incomplete_opened_payload(self):
        response = self.deliver({"action": "opened"})

        self.assertEqual(400, response.status)
        self.assertIn("missing required fields", response.message)

    def test_rejects_invalid_field_types(self):
        payload = opened_payload()
        payload["pull_request"]["number"] = "42"
        response = self.deliver(payload)

        self.assertEqual(400, response.status)
        self.assertIn("invalid field types", response.message)


class HttpHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(SECRET))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(*self.server.server_address)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        response_body = json.loads(response.read())
        connection.close()
        return response.status, response_body

    def test_health_endpoint(self):
        status, body = self.request("GET", "/health")

        self.assertEqual(200, status)
        self.assertEqual({"result": "ok", "message": "Listener is ready"}, body)

    def test_webhook_endpoint_processes_delivery(self):
        body = encode(opened_payload())
        status, response = self.request(
            "POST",
            "/webhook",
            body,
            {
                "Content-Type": "application/json",
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": sign(body),
            },
        )

        self.assertEqual(202, status)
        self.assertEqual("processed", response["result"])


if __name__ == "__main__":
    unittest.main()
