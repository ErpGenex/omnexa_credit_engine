import frappe
from frappe.tests.utils import FrappeTestCase

from omnexa_credit_engine.governance import (
	create_audit_snapshot,
	governance_overview,
	list_audit_snapshots,
	list_policy_versions,
	submit_policy_version,
)


class TestCreditEngineGovernance(FrappeTestCase):
	def test_submit_policy_and_snapshot(self):
		version = "v-test-" + frappe.generate_hash(length=8)
		submit_policy_version(
			"omnexa_credit_engine",
			policy_name="pricing_policy",
			version=version,
			payload={"spread_floor": 0.02
	},
			effective_from="2026-01-01",
		)
		pols = list_policy_versions("omnexa_credit_engine", policy_name="pricing_policy")
		self.assertTrue(pols)
		self.assertEqual(pols[-1]["status"], "PENDING_APPROVAL")

		create_audit_snapshot(
			"omnexa_credit_engine",
			process_name="decision_preview",
			inputs={"score": 700
	},
			outputs={"decision": "APPROVE"
	},
			policy_ref="pricing_policy:v-test-1",
		)
		snaps = list_audit_snapshots("omnexa_credit_engine", process_name="decision_preview", limit=10)
		self.assertTrue(snaps)

		ov = governance_overview("omnexa_credit_engine")
		self.assertGreaterEqual(ov["policies_total"], 1)
		self.assertGreaterEqual(ov["snapshots_total"], 1)
