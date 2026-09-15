import json, unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
import dispatch


class DispatchV12Tests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / "control" / "dispatch-policy.json").read_text())
        self.route_plan = json.loads((ROOT / "dispatch" / "pilot" / "route-plan.json").read_text())
        self.pilot = json.loads((ROOT / "dispatch" / "pilot" / "dispatch-envelope.json").read_text())
        self.abacus_route_plan = json.loads((ROOT / "dispatch" / "pilot" / "abacus-route-plan.json").read_text())
        self.abacus_pilot = json.loads((ROOT / "dispatch" / "pilot" / "abacus-dispatch-envelope.json").read_text())

    def test_cryoplant_pilot_envelope_is_deterministic_and_valid(self):
        route = self.route_plan["assignments"][0]
        built = dispatch.envelope(route, "GBOGEB/cryoplant-project", pilot=True)
        self.assertEqual(built, self.pilot)
        self.assertEqual(dispatch.validate_envelope(built, self.policy), [])

    def test_abacus_dow_pilot_envelope_is_deterministic_and_valid(self):
        route = self.abacus_route_plan["assignments"][0]
        built = dispatch.envelope(route, "GBOGEB/ABACUS", pilot=True)
        self.assertEqual(built, self.abacus_pilot)
        self.assertEqual(dispatch.validate_envelope(built, self.policy), [])

    def test_tamper_breaks_digest(self):
        bad = dict(self.abacus_pilot)
        bad["crew"] = "CAUSAL_TRIAGE"
        self.assertIn("ENVELOPE_DIGEST_MISMATCH", dispatch.validate_envelope(bad, self.policy))

    def test_empty_live_route_plan_dispatches_nothing(self):
        p = dispatch.plan({"schema":"gloob-causal-route-plan/0.2","assignments":[]}, self.policy)
        self.assertEqual(p["dispatch_count"], 0)
        self.assertEqual(p["envelopes"], [])


if __name__ == "__main__": unittest.main()
