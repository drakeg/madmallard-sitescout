import copy
import json
import unittest
from pathlib import Path

from scripts.check_builder_candidates import validate_registry


class BuilderRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(Path("docs/builder-candidates.json").read_text(encoding="utf-8"))

    def test_registry_has_source_verified_candidates(self):
        self.assertTrue(validate_registry(self.source))
        lookup={item["id"]:item for item in self.source["candidates"]}
        self.assertEqual(lookup["onlook"]["license"],"Apache-2.0")
        self.assertIn("Central Icons",lookup["onlook"]["commercial_note"])
        self.assertIn("Firecrawl API key",lookup["open-lovable"]["required_external"])
        self.assertEqual(lookup["openpage"]["required_external"],[])
        self.assertIn("Model weights",lookup["ollama"]["commercial_note"])

    def test_registry_rejects_duplicate_and_unverified_license(self):
        clone=copy.deepcopy(self.source)
        clone["candidates"].append(clone["candidates"][0])
        with self.assertRaises(ValueError):
            validate_registry(clone)
        clone=copy.deepcopy(self.source)
        clone["candidates"][0]["license"]="Unknown"
        with self.assertRaises(ValueError):
            validate_registry(clone)

    def test_registry_rejects_missing_source_evidence(self):
        clone=copy.deepcopy(self.source)
        clone["candidates"][0]["evidence"]=[]
        with self.assertRaises(ValueError):
            validate_registry(clone)
        clone=copy.deepcopy(self.source)
        clone["candidates"][0]["license_blob"]="unknown"
        with self.assertRaises(ValueError):
            validate_registry(clone)
