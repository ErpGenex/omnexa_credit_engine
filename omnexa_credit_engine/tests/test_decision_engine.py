from decimal import Decimal

from frappe.tests.utils import FrappeTestCase

from omnexa_credit_engine.engine import (
	ApplicantMetrics,
	CreditPolicy,
	DecisionContext,
	HybridModelSignals,
	evaluate_credit_decision,
)


class TestDecisionEngine(FrappeTestCase):
	def test_decline_when_score_below_policy(self):
		metrics = ApplicantMetrics(
			score=520,
			dti=Decimal("0.30"),
			ltv=Decimal("0.60"),
			request_amount=Decimal("5000"),
			current_exposure=Decimal("1000"),
		)
		out = evaluate_credit_decision(metrics, CreditPolicy(min_score=600))
		self.assertEqual(out.decision, "DECLINE")
		self.assertIn("score_below_policy", out.reasons)
		self.assertTrue(any(rc.get("code") == "CRD-SCORE-001" for rc in out.reason_codes))
		self.assertTrue(out.decision_matrix_path.startswith("MATRIX_"))

	def test_review_when_only_dti_breach(self):
		metrics = ApplicantMetrics(
			score=700,
			dti=Decimal("0.55"),
			ltv=Decimal("0.60"),
			request_amount=Decimal("5000"),
			current_exposure=Decimal("1000"),
		)
		out = evaluate_credit_decision(metrics)
		self.assertEqual(out.decision, "REVIEW")
		self.assertIn("dti_above_policy", out.reasons)
		self.assertTrue(any(rc.get("code") == "CRD-DTI-002" for rc in out.reason_codes))

	def test_hybrid_model_signal_reason_codes(self):
		metrics = ApplicantMetrics(
			score=710,
			dti=Decimal("0.25"),
			ltv=Decimal("0.55"),
			request_amount=Decimal("5000"),
			current_exposure=Decimal("1000"),
		)
		out = evaluate_credit_decision(
			metrics,
			hybrid=HybridModelSignals(model_score=Decimal("0.40"), model_confidence=Decimal("0.50"), model_name="xgb-v1"),
			context=DecisionContext(portfolio_name="Retail", response_target_ms=200),
		)
		self.assertIn(out.decision, ("REVIEW", "DECLINE"))
		self.assertTrue(any(rc.get("code") == "CRD-ML-005" for rc in out.reason_codes))
		self.assertTrue(any(rc.get("code") == "CRD-ML-006" for rc in out.reason_codes))

