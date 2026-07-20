from frappe.tests.utils import FrappeTestCase

import frappe

from omnexa_core.tests.test_helpers import suppress_workflow_attach_print

suppress_workflow_attach_print()

from omnexa_credit_engine.api import evaluate_decision, evaluate_decision_advanced, upsert_credit_decision_case


class TestDecisionApi(FrappeTestCase):
	def test_evaluate_decision_api(self):
		out = evaluate_decision(
			score=710,
			dti="0.32",
			ltv="0.70",
			request_amount="12000",
			current_exposure="5000",
		)
		self.assertIn(out["decision"], ("APPROVE", "REVIEW", "DECLINE"))
		self.assertIn("risk_grade", out)
		self.assertIn("approved_limit", out)

	def test_advanced_decision_and_case_upsert(self):
		profile = frappe.get_doc(
			{
				"doctype": "Credit Rule Profile",
				"profile_name": f"Retail-EG-{frappe.generate_hash(length=6)
	}",
				"status": "ACTIVE",
				"country_code": "EG",
				"product_code": "VEHICLE",
				"customer_segment": "SALARIED",
				"portfolio_name": "Retail",
				"min_score": 640,
				"max_dti": 0.45,
				"max_ltv": 0.85,
				"max_exposure": 750000,
				"risk_appetite_level": "BALANCED"
	}
		)
		profile.insert(ignore_permissions=True)

		out = evaluate_decision_advanced(
			score=700,
			dti="0.30",
			ltv="0.70",
			request_amount="12000",
			current_exposure="5000",
			country_code="EG",
			product_code="VEHICLE",
			customer_segment="SALARIED",
			model_score="0.72",
			model_confidence="0.89",
			model_name="hybrid-v2",
		)
		self.assertIn("decision", out)
		self.assertIn("policy_source", out)
		self.assertIn("integration", out)

		case_out = upsert_credit_decision_case(
			customer_name="Decision Case Test",
			score=700,
			dti="0.30",
			ltv="0.70",
			request_amount="12000",
			current_exposure="5000",
			country_code="EG",
			product_code="VEHICLE",
			customer_segment="SALARIED",
		)
		self.assertIn("case_id", case_out)
		self.assertTrue(case_out["case_id"])

