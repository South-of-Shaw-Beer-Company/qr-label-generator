"""Real CLI/PDF regressions for dependency security updates (no mocks)."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.generate_labels import PdfReader, generate_qr_code


class LabelGenerationTests(unittest.TestCase):
    def generate(self, directory, *arguments):
        output = Path(directory) / "nested" / "labels.pdf"
        result = subprocess.run(
            [sys.executable, str(ROOT / "src/generate_labels.py"),
             "--base-url", "https://example.com/keg/scan/", "--output", str(output),
             *arguments],
            cwd=ROOT, capture_output=True, text=True, timeout=60, check=True,
        )
        self.assertIn("Successfully created", result.stdout)
        self.assertTrue(output.read_bytes().startswith(b"%PDF-"))
        return PdfReader(str(output))

    def assert_letter_pages(self, reader, count):
        self.assertEqual(len(reader.pages), count)
        for page in reader.pages:
            self.assertAlmostEqual(float(page.mediabox.width), 612)
            self.assertAlmostEqual(float(page.mediabox.height), 792)

    def test_plain_labels_preserve_sequence_across_partial_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            reader = self.generate(directory, "--count", "25", "--start", "100",
                                   "--prefix", "KEG-", "--no-template")
            self.assert_letter_pages(reader, 2)
            for page, numbers in zip(reader.pages, (range(100, 124), range(124, 125))):
                self.assertEqual(re.findall(r"KEG-\d{4}", page.extract_text()),
                                 [f"KEG-{number:04d}" for number in numbers])
                images = [obj.get_object() for obj in page["/Resources"]["/XObject"].values()
                          if obj.get_object().get("/Subtype") == "/Image"]
                self.assertEqual(len(images), len(numbers))
                self.assertTrue(all(int(image["/Width"]) > 0 for image in images))

    def test_template_sheet_keeps_all_label_text_and_artwork(self):
        with tempfile.TemporaryDirectory() as directory:
            reader = self.generate(directory, "--count", "24")
            self.assert_letter_pages(reader, 1)
            text = reader.pages[0].extract_text()
            self.assertEqual(re.findall(r"ITEM-\d{4}", text),
                             [f"ITEM-{number:04d}" for number in range(1, 25)])
            template = PdfReader(str(ROOT / "templates/SL655.pdf"))
            self.assertGreater(len(reader.pages[0].get_contents().get_data()),
                               len(template.pages[0].get_contents().get_data()))

    def test_qr_image_is_a_real_nonempty_png(self):
        image = generate_qr_code("https://example.com/item/ITEM-0001").get_image()
        self.assertGreater(image.width, 0)
        self.assertEqual(image.width, image.height)
        self.assertEqual(image.convert("L").getextrema(), (0, 255))

    def test_pdf_comment_at_eof_does_not_hang(self):
        # GHSA-4vvm-4w3v-6mr8: PyPDF2 loops forever on an EOF comment.
        # Use the same PDF implementation imported by the actual CLI.
        program = """
import importlib
from src.generate_labels import PdfReader
family = PdfReader.__module__.split('.')[0]
generic = importlib.import_module(family + '.generic')
stream = generic.DecodedStreamObject()
stream.set_data(b'% comment without a trailing newline')
generic.ContentStream(stream, None)
print('parsed')
"""
        try:
            result = subprocess.run([sys.executable, "-c", program], cwd=ROOT,
                                    capture_output=True, text=True, timeout=5, check=True)
        except subprocess.TimeoutExpired:
            self.fail("The CLI's PDF dependency hangs parsing an EOF comment")
        self.assertEqual(result.stdout.strip(), "parsed")

    def test_cli_rejects_missing_required_arguments(self):
        result = subprocess.run([sys.executable, str(ROOT / "src/generate_labels.py")],
                                cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--count", result.stderr)
        self.assertIn("--base-url", result.stderr)


if __name__ == "__main__":
    unittest.main()
