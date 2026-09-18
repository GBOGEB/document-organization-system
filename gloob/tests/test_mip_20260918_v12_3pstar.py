import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "mip" / "2026-09-18-v12-control" / "01_3PSTAR_STATUS.yaml"
EXECUTIVE = ROOT / "mip" / "2026-09-18-v12-control" / "00_3PSTAR_EXECUTIVE.md"

class TestV12ThreePStarReceipt(unittest.TestCase):
    def test_receipt_pins_control_proof(self):
        text = RECEIPT.read_text(encoding="utf-8")
        self.assertIn("overall: PASS", text)
        self.assertIn("220f612bc7d0975a592c587817059428b826c6b6", text)
        self.assertIn("34936608687", text)
        self.assertIn("34936607875", text)
        self.assertIn("QPLANT_RESPONDER_RUNTIME_HARDENING", text)

    def test_no_authority_credit_leak(self):
        text = RECEIPT.read_text(encoding="utf-8")
        self.assertIn("control_credit: false", text)
        self.assertIn("engineering_acceptance_credit: false", text)
        self.assertIn("commercial_credit: false", text)
        self.assertIn("No v1.3 fan-out", EXECUTIVE.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
