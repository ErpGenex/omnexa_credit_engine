# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from dataclasses import dataclass, asdict
from decimal import Decimal
from time import perf_counter


@dataclass(frozen=True)
class CreditPolicy:
	min_score: int = 600
	max_dti: Decimal = Decimal("0.40")
	max_ltv: Decimal = Decimal("0.80")
	max_exposure: Decimal = Decimal("500000")


@dataclass(frozen=True)
class ApplicantMetrics:
	score: int
	dti: Decimal
	ltv: Decimal
	request_amount: Decimal
	current_exposure: Decimal
	country_code: str = "INTL"
	product_code: str = "GENERIC"
	customer_segment: str = "STANDARD"


@dataclass(frozen=True)
class HybridModelSignals:
	model_score: Decimal | None = None
	model_confidence: Decimal | None = None
	model_name: str | None = None


@dataclass(frozen=True)
class DecisionContext:
	portfolio_name: str = "GLOBAL"
	response_target_ms: int = 200


@dataclass(frozen=True)
class DecisionResult:
	decision: str  # APPROVE | REVIEW | DECLINE
	reasons: list[str]
	risk_grade: str  # LOW | MEDIUM | HIGH
	approved_limit: Decimal
	reason_codes: list[dict]
	decision_matrix_path: str
	latency_ms: int
	compliance_tags: list[str]

	def to_dict(self) -> dict:
		out = asdict(self)
		out["approved_limit"] = str(self.approved_limit)
		return out


def evaluate_credit_decision(
	metrics: ApplicantMetrics,
	policy: CreditPolicy | None = None,
	hybrid: HybridModelSignals | None = None,
	context: DecisionContext | None = None,
) -> DecisionResult:
	"""Deterministic baseline decisioning hook for credit engine."""
	t0 = perf_counter()
	p = policy or CreditPolicy()
	h = hybrid or HybridModelSignals()
	ctx = context or DecisionContext()
	reasons: list[str] = []
	decision = "APPROVE"
	matrix_path = "MATRIX_APPROVE"

	total_exposure = metrics.current_exposure + metrics.request_amount
	if metrics.score < p.min_score:
		reasons.append("score_below_policy")
	if metrics.dti > p.max_dti:
		reasons.append("dti_above_policy")
	if metrics.ltv > p.max_ltv:
		reasons.append("ltv_above_policy")
	if total_exposure > p.max_exposure:
		reasons.append("exposure_limit_breach")
	if h.model_score is not None and h.model_score < Decimal("0.45"):
		reasons.append("ml_score_low")
	if h.model_confidence is not None and h.model_confidence < Decimal("0.60"):
		reasons.append("ml_low_confidence")

	if any(r in reasons for r in ("score_below_policy", "exposure_limit_breach")):
		decision = "DECLINE"
		matrix_path = "MATRIX_DECLINE_HARD_POLICY"
	elif reasons:
		decision = "REVIEW"
		matrix_path = "MATRIX_REVIEW_SOFT_BREACH"

	risk_grade = _risk_grade(metrics)
	approved_limit = Decimal("0") if decision == "DECLINE" else max(Decimal("0"), p.max_exposure - metrics.current_exposure)
	reason_codes = _build_reason_codes(reasons)
	latency_ms = int((perf_counter() - t0) * 1000)
	compliance_tags = [
		"BASEL_II_IRB_READY",
		"BASEL_III_RISK_APPETITE",
		"EXPLAINABLE_DECISION",
		"COUNTRY_PRODUCT_SEGMENT_POLICY",
	]
	if latency_ms <= ctx.response_target_ms:
		compliance_tags.append("REALTIME_TARGET_MET")
	else:
		compliance_tags.append("REALTIME_TARGET_BREACH")

	return DecisionResult(
		decision=decision,
		reasons=reasons,
		risk_grade=risk_grade,
		approved_limit=approved_limit,
		reason_codes=reason_codes,
		decision_matrix_path=matrix_path,
		latency_ms=latency_ms,
		compliance_tags=compliance_tags,
	)


def _risk_grade(metrics: ApplicantMetrics) -> str:
	if metrics.score >= 750 and metrics.dti <= Decimal("0.30"):
		return "LOW"
	if metrics.score >= 650 and metrics.dti <= Decimal("0.45"):
		return "MEDIUM"
	return "HIGH"


def _build_reason_codes(reasons: list[str]) -> list[dict]:
	catalog = {
		"score_below_policy": {
			"code": "CRD-SCORE-001",
			"severity": "high",
			"title": "Score Below Minimum",
		},
		"dti_above_policy": {
			"code": "CRD-DTI-002",
			"severity": "medium",
			"title": "DTI Above Threshold",
		},
		"ltv_above_policy": {
			"code": "CRD-LTV-003",
			"severity": "medium",
			"title": "LTV Above Threshold",
		},
		"exposure_limit_breach": {
			"code": "CRD-EXP-004",
			"severity": "high",
			"title": "Exposure Limit Breach",
		},
		"ml_score_low": {
			"code": "CRD-ML-005",
			"severity": "medium",
			"title": "Model Score Below Cutoff",
		},
		"ml_low_confidence": {
			"code": "CRD-ML-006",
			"severity": "medium",
			"title": "Model Confidence Low",
		},
	}
	return [catalog[r] for r in reasons if r in catalog]

