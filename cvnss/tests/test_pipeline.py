"""Kiểm thử độc lập đường dữ liệu và CVNSS4.0 (không cần mô hình đã học)."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from cvnss.prepare import prepare, read_pairs
from cvnss.tokenizer import build


class DataPipelineTests(unittest.TestCase):
    def test_clean_and_split_reproducible(self):
        self.assertEqual(len(read_pairs(None)), 50)
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            count_a = prepare("unicode", out_dir=first)
            count_b = prepare("unicode", out_dir=second)
            self.assertEqual(count_a, {"train": 40, "val": 5, "test": 5})
            self.assertEqual(count_a, count_b)
            for name in ("train", "val", "test"):
                self.assertEqual((Path(first) / f"{name}.jsonl").read_bytes(),
                                 (Path(second) / f"{name}.jsonl").read_bytes())
            self.assertEqual(json.loads((Path(first) / "manifest.json").read_text())["seed"], 42)

    @unittest.skipUnless(shutil.which("node"), "Cần Node.js")
    def test_converter_and_cvnss_split(self):
        with tempfile.TemporaryDirectory() as directory:
            count = prepare("cvnss", out_dir=directory)
            self.assertEqual(sum(count.values()), 50)
            rows = [json.loads(line) for line in (Path(directory)/"train.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(isinstance(row["prompt"], str) and isinstance(row["completion"], str) for row in rows))
        proc = subprocess.run(["node", "-e",
                               "const c=require('./cvnss/vendor/converter.js');console.log(JSON.stringify(c.selfTest()))"],
                              capture_output=True, text=True, check=True)
        audit = json.loads(proc.stdout)
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["tests"], 23)

    def test_validation_of_bad_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"invalid.jsonl"
            p.write_text('{"prompt":"hi"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_pairs(str(p))

if __name__ == "__main__":
    unittest.main()
