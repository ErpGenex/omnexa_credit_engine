# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import hashlib
import json

import frappe


ALLOWED_CHECKER_ROLES = {"System Manager", "Compliance Manager", "Risk Manager"}
BACKEND = {'omnexa_finance_engine': {'policy_doctype': 'Finance Policy Version', 'snapshot_doctype': 'Finance Audit Snapshot'}, 'omnexa_credit_engine': {'policy_doctype': 'Credit Policy Version', 'snapshot_doctype': 'Credit Audit Snapshot'}, 'omnexa_credit_risk': {'policy_doctype': 'Credit Risk Policy Version', 'snapshot_doctype': 'Credit Risk Audit Snapshot'}, 'omnexa_operational_risk': {'policy_doctype': 'Operational Risk Policy Version', 'snapshot_doctype': 'Operational Risk Audit Snapshot'}, 'omnexa_alm': {'policy_doctype': 'ALM Policy Version', 'snapshot_doctype': 'ALM Audit Snapshot'}, 'omnexa_consumer_finance': {'policy_doctype': 'Consumer Finance Policy Version', 'snapshot_doctype': 'Consumer Finance Audit Snapshot'}, 'omnexa_vehicle_finance': {'policy_doctype': 'Vehicle Finance Policy Version', 'snapshot_doctype': 'Vehicle Finance Audit Snapshot'}, 'omnexa_mortgage_finance': {'policy_doctype': 'Mortgage Finance Policy Version', 'snapshot_doctype': 'Mortgage Finance Audit Snapshot'}, 'omnexa_factoring': {'policy_doctype': 'Factoring Policy Version', 'snapshot_doctype': 'Factoring Audit Snapshot'}, 'omnexa_sme_retail_finance': {'policy_doctype': 'SME Retail Finance Policy Version', 'snapshot_doctype': 'SME Retail Finance Audit Snapshot'}}


def _policy_key(app: str) -> str:
	return f"{app}_policy_registry_json"


def _snapshot_key(app: str) -> str:
	return f"{app}_audit_snapshots_json"


def _policy_doctype(app: str) -> str:
	return BACKEND[app]["policy_doctype"]


def _snapshot_doctype(app: str) -> str:
	return BACKEND[app]["snapshot_doctype"]


def _nowts() -> str:
	return frappe.utils.now_datetime().replace(microsecond=0).isoformat(sep=" ")


def _load_json_default(key: str) -> list[dict]:
	raw = frappe.db.get_default(key)
	if not raw:
		return []
	try:
		val = json.loads(str(raw))
		return val if isinstance(val, list) else []
	except Exception:
		return []


def _save_json_default(key: str, rows: list[dict]) -> None:
	frappe.db.set_default(key, json.dumps(rows, separators=(",", ":"), sort_keys=True))
	frappe.db.commit()


def _require_checker_role() -> None:
	roles = set(frappe.get_roles() or [])
	if not (roles & ALLOWED_CHECKER_ROLES):
		frappe.throw(frappe._("You do not have checker approval role."))


def _has_doctype_backend(app: str) -> bool:
	return bool(frappe.db.exists("DocType", _policy_doctype(app)))


def _parse_json(raw: str | None) -> dict:
	if not raw:
		return {}
	try:
		val = json.loads(str(raw))
		return val if isinstance(val, dict) else {}
	except Exception:
		return {}


def _policy_doc_to_dict(doc) -> dict:
	return {
		"name": doc.name,
		"policy_name": doc.policy_name,
		"version": doc.policy_version,
		"payload": _parse_json(getattr(doc, "payload_json", None)),
		"effective_from": getattr(doc, "effective_from", None),
		"status": getattr(doc, "status", None),
		"maker": getattr(doc, "maker", None),
		"checker": getattr(doc, "checker", None),
		"rejector": getattr(doc, "rejector", None),
		"created_at": getattr(doc, "created_at", None),
		"approved_at": getattr(doc, "approved_at", None),
		"rejected_at": getattr(doc, "rejected_at", None),
		"rejection_reason": getattr(doc, "rejection_reason", None),
	}


def submit_policy_version(app: str, policy_name: str, version: str, payload: dict, effective_from: str | None = None) -> dict:
	if _has_doctype_backend(app):
		dt = _policy_doctype(app)
		exists = frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version})
		if exists:
			frappe.throw(frappe._("Policy version already exists."))
		doc = frappe.get_doc(
			{
				"doctype": dt,
				"policy_name": policy_name,
				"policy_version": version,
				"payload_json": json.dumps(payload, separators=(",", ":"), sort_keys=True),
				"effective_from": effective_from,
				"status": "PENDING_APPROVAL",
				"maker": frappe.session.user,
				"created_at": _nowts(),
			}
		)
		doc.insert(ignore_permissions=True)
		return _policy_doc_to_dict(doc)

	rows = _load_json_default(_policy_key(app))
	if any(r.get("policy_name") == policy_name and r.get("version") == version for r in rows):
		frappe.throw(frappe._("Policy version already exists."))
	now = _nowts()
	entry = {
		"policy_name": policy_name,
		"version": version,
		"payload": payload,
		"effective_from": effective_from,
		"status": "PENDING_APPROVAL",
		"maker": frappe.session.user,
		"checker": None,
		"rejector": None,
		"created_at": now,
		"approved_at": None,
		"rejected_at": None,
		"rejection_reason": None,
	}
	rows.append(entry)
	_save_json_default(_policy_key(app), rows)
	return entry


def approve_policy_version(app: str, policy_name: str, version: str) -> dict:
	_require_checker_role()
	if _has_doctype_backend(app):
		dt = _policy_doctype(app)
		name = frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version})
		if not name:
			frappe.throw(frappe._("Policy version not found."))
		doc = frappe.get_doc(dt, name)
		if doc.status == "APPROVED":
			return _policy_doc_to_dict(doc)
		if doc.maker == frappe.session.user:
			frappe.throw(frappe._("Maker and checker must be different users."))
		doc.status = "APPROVED"
		doc.checker = frappe.session.user
		doc.approved_at = _nowts()
		doc.save(ignore_permissions=True)
		return _policy_doc_to_dict(doc)

	rows = _load_json_default(_policy_key(app))
	for r in rows:
		if r.get("policy_name") == policy_name and r.get("version") == version:
			if r.get("status") == "APPROVED":
				return r
			if r.get("maker") == frappe.session.user:
				frappe.throw(frappe._("Maker and checker must be different users."))
			r["status"] = "APPROVED"
			r["checker"] = frappe.session.user
			r["approved_at"] = _nowts()
			_save_json_default(_policy_key(app), rows)
			return r
	frappe.throw(frappe._("Policy version not found."))


def reject_policy_version(app: str, policy_name: str, version: str, reason: str = "") -> dict:
	_require_checker_role()
	if _has_doctype_backend(app):
		dt = _policy_doctype(app)
		name = frappe.db.exists(dt, {"policy_name": policy_name, "policy_version": version})
		if not name:
			frappe.throw(frappe._("Policy version not found."))
		doc = frappe.get_doc(dt, name)
		if doc.maker == frappe.session.user:
			frappe.throw(frappe._("Maker and checker must be different users."))
		doc.status = "REJECTED"
		doc.rejector = frappe.session.user
		doc.rejected_at = _nowts()
		doc.rejection_reason = reason or ""
		doc.save(ignore_permissions=True)
		return _policy_doc_to_dict(doc)

	rows = _load_json_default(_policy_key(app))
	for r in rows:
		if r.get("policy_name") == policy_name and r.get("version") == version:
			if r.get("maker") == frappe.session.user:
				frappe.throw(frappe._("Maker and checker must be different users."))
			r["status"] = "REJECTED"
			r["rejector"] = frappe.session.user
			r["rejected_at"] = _nowts()
			r["rejection_reason"] = reason or ""
			_save_json_default(_policy_key(app), rows)
			return r
	frappe.throw(frappe._("Policy version not found."))


def list_policy_versions(app: str, policy_name: str | None = None) -> list[dict]:
	if _has_doctype_backend(app):
		filters = {}
		if policy_name:
			filters["policy_name"] = policy_name
		names = frappe.get_all(_policy_doctype(app), filters=filters, order_by="creation asc", pluck="name")
		return [_policy_doc_to_dict(frappe.get_doc(_policy_doctype(app), n)) for n in names]
	rows = _load_json_default(_policy_key(app))
	if policy_name:
		rows = [r for r in rows if r.get("policy_name") == policy_name]
	return rows


def create_audit_snapshot(app: str, process_name: str, inputs: dict, outputs: dict, policy_ref: str | None = None) -> dict:
	if _has_doctype_backend(app):
		now = _nowts()
		payload = {
			"process_name": process_name,
			"inputs": inputs,
			"outputs": outputs,
			"policy_ref": policy_ref,
			"actor": frappe.session.user,
			"created_at": now,
		}
		serial = json.dumps(payload, separators=(",", ":"), sort_keys=True)
		snapshot_hash = hashlib.sha256(serial.encode("utf-8")).hexdigest()
		doc = frappe.get_doc(
			{
				"doctype": _snapshot_doctype(app),
				"process_name": process_name,
				"policy_ref": policy_ref,
				"inputs_json": json.dumps(inputs, separators=(",", ":"), sort_keys=True),
				"outputs_json": json.dumps(outputs, separators=(",", ":"), sort_keys=True),
				"snapshot_hash": snapshot_hash,
				"actor": frappe.session.user,
				"created_at": now,
			}
		)
		doc.insert(ignore_permissions=True)
		payload["snapshot_hash"] = snapshot_hash
		return payload

	rows = _load_json_default(_snapshot_key(app))
	now = _nowts()
	payload = {
		"process_name": process_name,
		"inputs": inputs,
		"outputs": outputs,
		"policy_ref": policy_ref,
		"actor": frappe.session.user,
		"created_at": now,
	}
	serial = json.dumps(payload, separators=(",", ":"), sort_keys=True)
	payload["snapshot_hash"] = hashlib.sha256(serial.encode("utf-8")).hexdigest()
	rows.append(payload)
	rows = rows[-500:]
	_save_json_default(_snapshot_key(app), rows)
	return payload


def list_audit_snapshots(app: str, process_name: str | None = None, limit: int = 100) -> list[dict]:
	if _has_doctype_backend(app):
		filters = {}
		if process_name:
			filters["process_name"] = process_name
		rows = frappe.get_all(
			_snapshot_doctype(app),
			filters=filters,
			fields=["process_name", "policy_ref", "inputs_json", "outputs_json", "snapshot_hash", "actor", "created_at"],
			order_by="creation asc",
		)
		out = []
		for r in rows[-int(limit):]:
			out.append({
				"process_name": r.process_name,
				"policy_ref": r.policy_ref,
				"inputs": _parse_json(r.inputs_json),
				"outputs": _parse_json(r.outputs_json),
				"snapshot_hash": r.snapshot_hash,
				"actor": r.actor,
				"created_at": r.created_at,
			})
		return out
	rows = _load_json_default(_snapshot_key(app))
	if process_name:
		rows = [r for r in rows if r.get("process_name") == process_name]
	return rows[-int(limit):]


def governance_overview(app: str) -> dict:
	policies = list_policy_versions(app)
	snaps = list_audit_snapshots(app, limit=500)
	return {
		"app": app,
		"policies_total": len(policies),
		"policies_pending": sum(1 for p in policies if p.get("status") == "PENDING_APPROVAL"),
		"policies_approved": sum(1 for p in policies if p.get("status") == "APPROVED"),
		"policies_rejected": sum(1 for p in policies if p.get("status") == "REJECTED"),
		"snapshots_total": len(snaps),
	}
