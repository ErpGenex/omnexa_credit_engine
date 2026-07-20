# Copyright (c) 2026, Omnexa and contributors

import json

from frappe.tests.utils import FrappeTestCase
import frappe

from omnexa_core.tests.test_helpers import suppress_workflow_attach_print

suppress_workflow_attach_print()

from omnexa_credit_engine.api import (
	approve_credit_decision_override,
	approve_credit_scorecard_status_change,
	complete_credit_connector_request_stub,
	enqueue_credit_connector_request,
	route_credit_decision_path,
	submit_credit_decision_override,
	submit_credit_scorecard_status_change,
	upsert_credit_decision_case,
	upsert_credit_scorecard,
	upsert_credit_strategy_route,
)


class TestCreditEngineWave3(FrappeTestCase):
	def _ensure_user(self, email: str) -> None:
		if frappe.db.exists("User", email):
			return
		doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": "Checker",
				"send_welcome_email": 0,
				"enabled": 1
	}
		)
		doc.append("roles", {"role": "System Manager"
	})
		doc.insert(ignore_permissions=True)

	def test_scorecard_strategy_connector_and_override(self):
		code = f"SC-{frappe.generate_hash(length=6)}"
		upsert_credit_scorecard(
			scorecard_code=code,
			title="Retail v2",
			definition_json=json.dumps({"bins": [300, 600, 850]}),
			scorecard_version="2.1.0",
			country_code="EG",
			product_code="PL",
			channel="MOBILE",
		)
		submit_credit_scorecard_status_change(code, "ACTIVE")
		self._ensure_user("checker_wave3_credit@example.com")
		frappe.set_user("checker_wave3_credit@example.com")
		approve_credit_scorecard_status_change(code)
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("Credit Scorecard", code, "status"), "ACTIVE")

		sid = f"ST-{frappe.generate_hash(length=6)}"
		upsert_credit_strategy_route(
			strategy_code=sid,
			title="Champion/Challenger test",
			champion_tree_json=json.dumps({"id": "champion_root", "edges": []
	}),
			challenger_tree_json=json.dumps({"id": "challenger_root", "edges": []
	}),
			traffic_split_percent="25",
			country_code="EG",
			product_code="PL",
		)
		doc = frappe.get_doc("Credit Strategy Route", sid)
		doc.status = "ACTIVE"
		doc.save(ignore_permissions=True)
		routed = route_credit_decision_path(sid, subject_key="cust-001")
		self.assertIn(routed["arm"], ("CHAMPION", "CHALLENGER"))
		self.assertIn("explainability", routed)

		key = f"idemp-{frappe.generate_hash(length=8)}"
		a = enqueue_credit_connector_request("BUREAU", key, '{"national_id":"X"}')
		b = enqueue_credit_connector_request("BUREAU", key, '{"national_id":"X"}')
		self.assertFalse(a["deduplicated"])
		self.assertTrue(b["deduplicated"])
		complete_credit_connector_request_stub(a["name"], 1)
		self.assertEqual(frappe.db.get_value("Credit Connector Request", a["name"], "status"), "SUCCESS")

		case = upsert_credit_decision_case(customer_name="Override Customer", score=700, dti="0.2", ltv="0.5", request_amount="10000")
		cid = case["case_id"]
		submit_credit_decision_override(cid, "DECLINE", "manual review decline", sla_hours=12)
		ov = frappe.get_all("Credit Decision Override", filters={"decision_case": cid
	}, pluck="name", limit=1)
		self.assertTrue(ov)
		frappe.set_user("checker_wave3_credit@example.com")
		approve_credit_decision_override(ov[0])
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("Credit Decision Case", cid, "decision_status"), "DECLINE")
