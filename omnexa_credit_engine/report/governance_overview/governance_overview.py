# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	filters = prepare_filters(filters)
	extra = policy_version_filters(filters)
	columns = [
		{"label": _("App"), "fieldname": "app", "fieldtype": "Data", "width": 180},
		{"label": _("Policies Total"), "fieldname": "policies_total", "fieldtype": "Int", "width": 120},
		{"label": _("Pending"), "fieldname": "pending", "fieldtype": "Int", "width": 90},
		{"label": _("Approved"), "fieldname": "approved", "fieldtype": "Int", "width": 90},
		{"label": _("Rejected"), "fieldname": "rejected", "fieldtype": "Int", "width": 90},
	]
	snaps = 0

	base = extra or {}
	pol_total = frappe.db.count("Credit Policy Version", base or None)
	pending = frappe.db.count("Credit Policy Version", {**base, "status": "PENDING_APPROVAL"})
	approved = frappe.db.count("Credit Policy Version", {**base, "status": "APPROVED"})
	rejected = frappe.db.count("Credit Policy Version", {**base, "status": "REJECTED"})
	row = {
		"app": "omnexa_credit_engine",
		"policies_total": pol_total,
		"pending": pending,
		"approved": approved,
		"rejected": rejected,
	}
	if snaps:
		row["snapshots"] = snaps
	return columns, [row]
