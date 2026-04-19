# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe


def execute(filters=None):
	columns = [
		{{"label": "App", "fieldname": "app", "fieldtype": "Data", "width": 180}},
		{{"label": "Policies Total", "fieldname": "policies_total", "fieldtype": "Int", "width": 120}},
		{{"label": "Pending", "fieldname": "pending", "fieldtype": "Int", "width": 90}},
		{{"label": "Approved", "fieldname": "approved", "fieldtype": "Int", "width": 90}},
		{{"label": "Rejected", "fieldname": "rejected", "fieldtype": "Int", "width": 90}},
		{{"label": "Snapshots", "fieldname": "snapshots", "fieldtype": "Int", "width": 100}},
	]

	pol_total = frappe.db.count("Credit Policy Version")
	pending = frappe.db.count("Credit Policy Version", {{"status": "PENDING_APPROVAL"}})
	approved = frappe.db.count("Credit Policy Version", {{"status": "APPROVED"}})
	rejected = frappe.db.count("Credit Policy Version", {{"status": "REJECTED"}})
	snaps = frappe.db.count("Credit Audit Snapshot")

	data = [
		{{
			"app": "omnexa_credit_engine",
			"policies_total": pol_total,
			"pending": pending,
			"approved": approved,
			"rejected": rejected,
			"snapshots": snaps,
		}}
	]
	return columns, data
