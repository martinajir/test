import hashlib
import hmac
import json
import unittest

from pull_request_closed_listener import handle_webhook, verify_signature


SECRET = "test-webhook-secret"


def encode(payload):
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def sign(body, secret=SECRET):
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def closed_payload(merged=False):
    return {
        "action": "closed",
        "repository": {"full_name": "octocat/Hello-World"},
        "pull_request": {
            "number": 42,
            "title": "Improve the greeting",
            "merged": merged,
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

    def test_processes_closed_pull_request(self):
        response = self.deliver(closed_payload())

        self.assertEqual(202, response.status)
        self.assertEqual("processed", response.result)
        self.assertEqual(
            "Pull request #42 in octocat/Hello-World was closed without merging "
            "by monalisa: Improve the greeting",
            response.message,
        )

    def test_distinguishes_merged_pull_request(self):
        response = self.deliver(closed_payload(merged=True))

        self.assertEqual("processed", response.result)
        self.assertIn("was merged", response.message)

    def test_ignores_other_actions_and_events(self):
        opened = closed_payload()
        opened["action"] = "opened"

        self.assertEqual("ignored", self.deliver(opened).result)
        self.assertEqual(
            "ignored",
            self.deliver(closed_payload(), event="issues").result,
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

    def test_rejects_incomplete_closed_payload(self):
        response = self.deliver({"action": "closed"})

        self.assertEqual(400, response.status)
        self.assertIn("missing required fields", response.message)


if __name__ == "__main__":
    unittest.main()
