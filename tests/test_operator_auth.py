import hashlib
import json
import unittest
from unittest.mock import patch

from app.operator_auth import authenticate_operator, load_operator_digests


class OperatorAuthTests(unittest.TestCase):
    def setUp(self):
        self.alice = "a" * 40
        self.bob = "b" * 40
        self.config = json.dumps({
            "alice": hashlib.sha256(self.alice.encode()).hexdigest(),
            "bob": hashlib.sha256(self.bob.encode()).hexdigest(),
        })

    def test_identifies_actor_using_configured_token_digest(self):
        self.assertEqual(authenticate_operator(
            {"Authorization": "Bearer " + self.alice},
            configuration=self.config), (200, "alice"))
        self.assertEqual(authenticate_operator(
            {"Authorization": "Bearer " + self.bob},
            configuration=self.config), (200, "bob"))

    def test_rejects_missing_invalid_and_short_tokens(self):
        for header in ("", "Basic abc", "Bearer wrong", "Bearer " + "z" * 40,
                       "bearer " + self.alice, "Bearer " + "x" * 513):
            with self.subTest(header=header[:20]):
                self.assertEqual(authenticate_operator(
                    {"Authorization": header}, configuration=self.config), (401, None))

    def test_configuration_fail_closed(self):
        for value in ("", "null", "[]", "{}", "{bad json}",
                      json.dumps({"../admin": "0" * 64}),
                      json.dumps({"alice": "not-a-sha256"}),
                      json.dumps({"alice": "0" * 64, "bob": "0" * 64})):
            with self.subTest(value=value[:30]):
                self.assertEqual(authenticate_operator(
                    {"Authorization": "Bearer " + self.alice},
                    configuration=value), (503, None))
        with patch.dict("os.environ", {"SITESCOUT_OPERATOR_TOKEN_HASHES": ""}):
            self.assertEqual(authenticate_operator(
                {"Authorization": "Bearer " + self.alice}), (503, None))

    def test_loader_accepts_valid_mapping(self):
        self.assertEqual(set(load_operator_digests(self.config)), {"alice", "bob"})

    def test_no_error_discloses_credentials(self):
        self.assertEqual(authenticate_operator(
            {"Authorization": "Bearer " + self.alice},
            configuration='{"alice":"invalid"}'), (503, None))
