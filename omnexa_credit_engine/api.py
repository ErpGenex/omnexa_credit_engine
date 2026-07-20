# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

from decimal import Decimal
import json

import frappe

from .engine import (
	ApplicantMetrics,
	CreditPolicy,
	DecisionContext,
	HybridModelSignals,
	evaluate_credit_decision,
)
from .standards_profile import get_standards_profile as _get_standards_profile


@frappe.whitelist()
def get_standards_profile() -> dict:
	"""Expose standards profile for governance dashboards and audits."""
	return _get_standards_profile()


@frappe.whitelist()
def evaluate_decision(
	score: int,
	dti: str,
	ltv: str,
	request_amount: str,
	current_exposure: str = "0",
	min_score: int = 600,
	max_dti: str = "0.40",
	max_ltv: str = "0.80",
	max_exposure: str = "500000",
) -> dict:
	"""Baseline policy decision API (approve/review/decline with reasons)."""
	metrics = ApplicantMetrics(
		score=int(score),
		dti=Decimal(str(dti)),
		ltv=Decimal(str(ltv)),
		request_amount=Decimal(str(request_amount)),
		current_exposure=Decimal(str(current_exposure)),
	)
	policy = CreditPolicy(
		min_score=int(min_score),
		max_dti=Decimal(str(max_dti)),
		max_ltv=Decimal(str(max_ltv)),
		max_exposure=Decimal(str(max_exposure)),
	)
	return evaluate_credit_decision(metrics=metrics, policy=policy).to_dict()


def _resolve_credit_policy(country_code: str, product_code: str, customer_segment: str) -> tuple[CreditPolicy, str]:
	profile_name = frappe.db.exists(
		"Credit Rule Profile",
		{
			"status": "ACTIVE",
			"country_code": country_code,
			"product_code": product_code,
			"customer_segment": customer_segment
	},
	)
	if not profile_name:
		return CreditPolicy(), "default_policy_fallback"
	profile = frappe.get_doc("Credit Rule Profile", profile_name)
	return (
		CreditPolicy(
			min_score=int(profile.min_score or 600),
			max_dti=Decimal(str(profile.max_dti or "0.40")),
			max_ltv=Decimal(str(profile.max_ltv or "0.80")),
			max_exposure=Decimal(str(profile.max_exposure or "500000")),
		),
		profile.name,
	)


def _integration_payload(decision_out: dict, product_code: str, country_code: str) -> dict:
	# Lightweight, pluggable hints for downstream engines.
	return {
		"finance_engine": {
			"eligible": decision_out["decision"] in ("APPROVE", "REVIEW"),
			"approved_limit": decision_out["approved_limit"],
			"pricing_risk_grade": decision_out["risk_grade"],
			"product_code": product_code,
			"country_code": country_code
	},
		"credit_risk": {
			"risk_grade": decision_out["risk_grade"],
			"stage_hint": "STAGE_2" if decision_out["decision"] == "REVIEW" else "STAGE_1",
			"reason_codes": decision_out.get("reason_codes", [])},
	}


@frappe.whitelist()
def evaluate_decision_advanced(
	score: int,
	dti: str,
	ltv: str,
	request_amount: str,
	current_exposure: str = "0",
	country_code: str = "INTL",
	product_code: str = "GENERIC",
	customer_segment: str = "STANDARD",
	portfolio_name: str = "GLOBAL",
	model_score: str | None = None,
	model_confidence: str | None = None,
	model_name: str | None = None,
) -> dict:
	policy, policy_source = _resolve_credit_policy(country_code, product_code, customer_segment)
	metrics = ApplicantMetrics(
		score=int(score),
		dti=Decimal(str(dti)),
		ltv=Decimal(str(ltv)),
		request_amount=Decimal(str(request_amount)),
		current_exposure=Decimal(str(current_exposure)),
		country_code=country_code,
		product_code=product_code,
		customer_segment=customer_segment,
	)
	hybrid = HybridModelSignals(
		model_score=Decimal(str(model_score)) if model_score is not None else None,
		model_confidence=Decimal(str(model_confidence)) if model_confidence is not None else None,
		model_name=model_name,
	)
	context = DecisionContext(portfolio_name=portfolio_name, response_target_ms=200)
	result = evaluate_credit_decision(metrics=metrics, policy=policy, hybrid=hybrid, context=context).to_dict()
	result["policy_source"] = policy_source
	result["integration"] = _integration_payload(result, product_code=product_code, country_code=country_code)
	return result


@frappe.whitelist()
def upsert_credit_decision_case(
	case_id: str | None = None,
	customer_name: str | None = None,
	score: int = 0,
	dti: str = "0",
	ltv: str = "0",
	request_amount: str = "0",
	current_exposure: str = "0",
	country_code: str = "INTL",
	product_code: str = "GENERIC",
	customer_segment: str = "STANDARD",
	portfolio_name: str = "GLOBAL",
	model_score: str | None = None,
	model_confidence: str | None = None,
	model_name: str | None = None,
) -> dict:
	decision_out = evaluate_decision_advanced(
		score=score,
		dti=dti,
		ltv=ltv,
		request_amount=request_amount,
		current_exposure=current_exposure,
		country_code=country_code,
		product_code=product_code,
		customer_segment=customer_segment,
		portfolio_name=portfolio_name,
		model_score=model_score,
		model_confidence=model_confidence,
		model_name=model_name,
	)
	doc = (
		frappe.get_doc("Credit Decision Case", case_id)
		if case_id and frappe.db.exists("Credit Decision Case", case_id)
		else frappe.new_doc("Credit Decision Case")
	)
	doc.customer_name = customer_name or "Unknown Customer"
	doc.country_code = country_code
	doc.product_code = product_code
	doc.customer_segment = customer_segment
	doc.portfolio_name = portfolio_name
	doc.decision_status = decision_out["decision"]
	doc.score = int(score)
	doc.dti = Decimal(str(dti))
	doc.ltv = Decimal(str(ltv))
	doc.request_amount = Decimal(str(request_amount))
	doc.current_exposure = Decimal(str(current_exposure))
	doc.approved_limit = Decimal(str(decision_out["approved_limit"]))
	doc.risk_grade = decision_out["risk_grade"]
	doc.decision_matrix_path = decision_out.get("decision_matrix_path")
	doc.latency_ms = int(decision_out.get("latency_ms", 0))
	doc.reason_codes_json = json.dumps(decision_out.get("reason_codes", []), sort_keys=True)
	doc.compliance_tags_json = json.dumps(decision_out.get("compliance_tags", []), sort_keys=True)
	doc.integration_payload_json = json.dumps(decision_out.get("integration", {}), sort_keys=True)
	doc.save(ignore_permissions=True)
	return {"case_id": doc.name, "decision": decision_out
	}


@frappe.whitelist()
def submit_policy_version(policy_name: str, version: str, payload: str, effective_from: str | None = None) -> dict:
	import json
	from .governance import submit_policy_version as _submit
	obj = json.loads(payload) if isinstance(payload, str) else payload
	if not isinstance(obj, dict):
		frappe.throw(frappe._("payload must be a JSON object"))
	return _submit("omnexa_credit_engine", policy_name=policy_name, version=version, payload=obj, effective_from=effective_from)


@frappe.whitelist()
def approve_policy_version(policy_name: str, version: str) -> dict:
	from .governance import approve_policy_version as _approve
	return _approve("omnexa_credit_engine", policy_name=policy_name, version=version)


@frappe.whitelist()
def create_audit_snapshot(process_name: str, inputs: str, outputs: str, policy_ref: str | None = None) -> dict:
	import json
	from .governance import create_audit_snapshot as _snap
	in_obj = json.loads(inputs) if isinstance(inputs, str) else inputs
	out_obj = json.loads(outputs) if isinstance(outputs, str) else outputs
	if not isinstance(in_obj, dict) or not isinstance(out_obj, dict):
		frappe.throw(frappe._("inputs/outputs must be JSON objects"))
	return _snap("omnexa_credit_engine", process_name=process_name, inputs=in_obj, outputs=out_obj, policy_ref=policy_ref)


@frappe.whitelist()
def get_governance_overview() -> dict:
	from .governance import governance_overview as _overview
	return _overview("omnexa_credit_engine")


@frappe.whitelist()
def reject_policy_version(policy_name: str, version: str, reason: str = "") -> dict:
	from .governance import reject_policy_version as _reject
	return _reject("omnexa_credit_engine", policy_name=policy_name, version=version, reason=reason)


@frappe.whitelist()
def list_policy_versions(policy_name: str | None = None) -> list[dict]:
	from .governance import list_policy_versions as _list
	return _list("omnexa_credit_engine", policy_name=policy_name)


@frappe.whitelist()
def list_audit_snapshots(process_name: str | None = None, limit: int = 100) -> list[dict]:
	from .governance import list_audit_snapshots as _list
	return _list("omnexa_credit_engine", process_name=process_name, limit=int(limit))


@frappe.whitelist()
def upsert_credit_scorecard(
	scorecard_code: str,
	title: str,
	definition_json: str,
	scorecard_version: str = "1.0.0",
	country_code: str = "INTL",
	product_code: str = "GENERIC",
	channel: str = "OMNI",
) -> dict:
	if frappe.db.exists("Credit Scorecard", scorecard_code):
		doc = frappe.get_doc("Credit Scorecard", scorecard_code)
	else:
		doc = frappe.new_doc("Credit Scorecard")
		doc.scorecard_code = scorecard_code
	doc.title = title
	doc.definition_json = definition_json
	doc.scorecard_version = scorecard_version
	doc.country_code = country_code
	doc.product_code = product_code
	doc.channel = channel
	doc.save(ignore_permissions=True)
	return {"scorecard_code": scorecard_code, "name": doc.name
	}


@frappe.whitelist()
def submit_credit_scorecard_status_change(scorecard_code: str, proposed_status: str) -> dict:
	from frappe.utils import now_datetime

	allowed = {"DRAFT", "ACTIVE", "RETIRED"}
	if proposed_status not in allowed:
		frappe.throw(frappe._("Invalid scorecard status"))
	doc = frappe.get_doc("Credit Scorecard", scorecard_code)
	doc.pending_status = proposed_status
	doc.status_submitted_by = frappe.session.user
	doc.status_submitted_on = now_datetime()
	doc.status_approved_by = None
	doc.status_approved_on = None
	doc.save(ignore_permissions=True)
	return {"scorecard_code": scorecard_code, "pending_status": proposed_status
	}


@frappe.whitelist()
def approve_credit_scorecard_status_change(scorecard_code: str) -> dict:
	from frappe.utils import now_datetime

	doc = frappe.get_doc("Credit Scorecard", scorecard_code)
	if not doc.pending_status:
		frappe.throw(frappe._("No pending scorecard status"))
	if doc.status_submitted_by == frappe.session.user:
		frappe.throw(frappe._("Checker must differ from maker"))
	doc.status = doc.pending_status
	doc.pending_status = None
	doc.status_approved_by = frappe.session.user
	doc.status_approved_on = now_datetime()
	doc.save(ignore_permissions=True)
	return {"scorecard_code": scorecard_code, "status": doc.status
	}


@frappe.whitelist()
def upsert_credit_strategy_route(
	strategy_code: str,
	title: str,
	champion_tree_json: str,
	challenger_tree_json: str,
	traffic_split_percent: str = "10",
	country_code: str = "INTL",
	product_code: str = "GENERIC",
) -> dict:
	if frappe.db.exists("Credit Strategy Route", strategy_code):
		doc = frappe.get_doc("Credit Strategy Route", strategy_code)
	else:
		doc = frappe.new_doc("Credit Strategy Route")
		doc.strategy_code = strategy_code
	doc.title = title
	doc.champion_tree_json = champion_tree_json
	doc.challenger_tree_json = challenger_tree_json
	doc.traffic_split_percent = traffic_split_percent
	doc.country_code = country_code
	doc.product_code = product_code
	doc.save(ignore_permissions=True)
	return {"strategy_code": strategy_code, "name": doc.name
	}


@frappe.whitelist()
def route_credit_decision_path(strategy_code: str, subject_key: str = "") -> dict:
	import hashlib

	doc = frappe.get_doc("Credit Strategy Route", strategy_code)
	if doc.status != "ACTIVE":
		frappe.throw(frappe._("Strategy route must be ACTIVE"))
	h = int(hashlib.sha256(f"{strategy_code}:{subject_key}".encode("utf-8")).hexdigest(), 16)
	pct = float(doc.traffic_split_percent or 0)
	bucket = (h % 10000) / 100.0
	arm = "CHALLENGER" if bucket < pct else "CHAMPION"
	explain = {
		"strategy_code": strategy_code,
		"arm": arm,
		"traffic_split_percent": pct,
		"determinism_bucket": bucket
	}
	store = json.loads(doc.explainability_store_json or "[]")
	if not isinstance(store, list):
		store = []
	store.append({"subject_key": subject_key, "arm": arm, "bucket": bucket
	})
	doc.explainability_store_json = json.dumps(store[-500:], default=str)
	doc.save(ignore_permissions=True)
	return {"arm": arm, "explainability": explain
	}


@frappe.whitelist()
def submit_credit_decision_override(
	decision_case: str,
	proposed_decision: str,
	override_reason: str,
	sla_hours: int = 24,
) -> dict:
	from frappe.utils import add_to_date, now_datetime

	case = frappe.get_doc("Credit Decision Case", decision_case)
	doc = frappe.get_doc(
		{
			"doctype": "Credit Decision Override",
			"decision_case": decision_case,
			"original_decision": case.decision_status,
			"proposed_decision": proposed_decision,
			"override_reason": override_reason,
			"workflow_status": "PENDING",
			"sla_due": add_to_date(now_datetime(), hours=int(sla_hours)),
			"maker": frappe.session.user,
			"maker_on": now_datetime()
	}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "workflow_status": doc.workflow_status
	}


@frappe.whitelist()
def approve_credit_decision_override(override_name: str) -> dict:
	from frappe.utils import now_datetime

	doc = frappe.get_doc("Credit Decision Override", override_name)
	if doc.workflow_status != "PENDING":
		frappe.throw(frappe._("Override is not pending"))
	if doc.maker == frappe.session.user:
		frappe.throw(frappe._("Checker must differ from maker"))
	doc.workflow_status = "APPROVED"
	doc.checker = frappe.session.user
	doc.checker_on = now_datetime()
	doc.save(ignore_permissions=True)
	case = frappe.get_doc("Credit Decision Case", doc.decision_case)
	case.decision_status = doc.proposed_decision
	case.save(ignore_permissions=True)
	return {"name": override_name, "workflow_status": doc.workflow_status, "case": doc.decision_case
	}


@frappe.whitelist()
def enqueue_credit_connector_request(connector_kind: str, idempotency_key: str, request_payload: str) -> dict:
	existing = frappe.db.get_value(
		"Credit Connector Request",
		{"connector_kind": connector_kind, "idempotency_key": idempotency_key
	},
		["name", "status"],
		as_dict=True,
	)
	if existing:
		return {"name": existing.name, "status": existing.status, "deduplicated": True
	}
	doc = frappe.get_doc(
		{
			"doctype": "Credit Connector Request",
			"connector_kind": connector_kind,
			"idempotency_key": idempotency_key,
			"request_payload": request_payload,
			"status": "PENDING"
	}
	)
	doc.insert(ignore_permissions=True)
	return {"name": doc.name, "status": doc.status, "deduplicated": False
	}


@frappe.whitelist()
def retry_credit_connector_request(name: str) -> dict:
	doc = frappe.get_doc("Credit Connector Request", name)
	doc.retry_count = int(doc.retry_count or 0) + 1
	doc.status = "PENDING"
	doc.last_error = None
	doc.save(ignore_permissions=True)
	return {"name": name, "retry_count": doc.retry_count
	}


@frappe.whitelist()
def complete_credit_connector_request_stub(name: str, success: int = 1) -> dict:
	doc = frappe.get_doc("Credit Connector Request", name)
	doc.status = "SUCCESS" if int(success) else "FAILED"
	doc.response_payload = json.dumps({"ok": bool(int(success)), "stub": True
	}, sort_keys=True)
	doc.save(ignore_permissions=True)
	return {"name": name, "status": doc.status
	}


@frappe.whitelist()
def get_regulatory_dashboard() -> dict:
	"""Unified compliance dashboard payload for this app."""
	from .governance import governance_overview
	from .standards_profile import get_standards_profile
	std = get_standards_profile()
	gov = governance_overview("omnexa_credit_engine")
	return {
		"app": "omnexa_credit_engine",
		"standards": std.get("standards", []),
		"activity_controls": std.get("activity_controls", []),
		"governance": gov,
		"compliance_score": _compute_compliance_score(std=std, gov=gov)}


def _compute_compliance_score(std: dict, gov: dict) -> int:
	"""Simple normalized readiness score (0..100) for executive monitoring."""
	base = min(50, 5 * len(std.get("standards", [])))
	controls = min(30, 3 * len(std.get("activity_controls", [])))
	approved = int(gov.get("policies_approved", 0) or 0)
	pending = int(gov.get("policies_pending", 0) or 0)
	governance = min(20, approved * 2)
	if pending > 0:
		governance = max(0, governance - min(10, pending))
	return int(base + controls + governance)

@frappe.whitelist()
def preview_gl_posting(
	scenario: str | None = None,
	rou_asset: str = "0",
	lease_liability: str = "0",
	principal: str = "0",
	settlement_cash: str = "0",
) -> dict:
	"""SAP parity — GL preview (finance_engine bridge, no JE)."""
	from omnexa_finance_engine.fs_parity_bridge import preview_gl_for_vertical
	return preview_gl_for_vertical(
		"credit_engine",
		scenario=scenario,
		rou_asset=rou_asset,
		lease_liability=lease_liability,
		principal=principal,
		settlement_cash=settlement_cash,
	)



@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("credit_engine", scenario=scenario, params=params)
