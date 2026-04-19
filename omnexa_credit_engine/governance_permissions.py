# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

PRIVILEGED_ROLES = {"System Manager", "Compliance Manager", "Risk Manager"}


def _is_privileged(user: str | None = None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user) or [])
	return bool(roles & PRIVILEGED_ROLES)


def policy_query_conditions(user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	esc = frappe.db.escape(user)
	return f"(`tabCredit Policy Version`.maker = {esc} or `tabCredit Policy Version`.checker = {esc} or `tabCredit Policy Version`.rejector = {esc})"


def policy_has_permission(doc, user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	return (doc.get("maker") == user) or (doc.get("checker") == user) or (doc.get("rejector") == user)


def snapshot_query_conditions(user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return ""
	esc = frappe.db.escape(user)
	return f"`tabCredit Audit Snapshot`.actor = {esc}"


def snapshot_has_permission(doc, user=None):
	user = user or frappe.session.user
	if _is_privileged(user):
		return True
	return doc.get("actor") == user
