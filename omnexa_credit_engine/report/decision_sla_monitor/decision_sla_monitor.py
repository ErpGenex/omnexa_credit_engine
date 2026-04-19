from __future__ import annotations

import frappe


def execute(filters=None):
	columns = [
		{"label": "Decision", "fieldname": "decision_status", "fieldtype": "Data", "width": 130},
		{"label": "Cases", "fieldname": "cases", "fieldtype": "Int", "width": 100},
		{"label": "Avg Latency (ms)", "fieldname": "avg_latency_ms", "fieldtype": "Float", "width": 140},
		{"label": "Max Latency (ms)", "fieldname": "max_latency_ms", "fieldtype": "Int", "width": 140},
		{"label": "SLA Breaches (>200ms)", "fieldname": "sla_breaches", "fieldtype": "Int", "width": 170},
	]

	rows = frappe.db.sql(
		"""
		select
			ifnull(decision_status, 'UNKNOWN') as decision_status,
			count(*) as cases,
			avg(ifnull(latency_ms, 0)) as avg_latency_ms,
			max(ifnull(latency_ms, 0)) as max_latency_ms,
			sum(case when ifnull(latency_ms, 0) > 200 then 1 else 0 end) as sla_breaches
		from `tabCredit Decision Case`
		group by decision_status
		order by cases desc
		""",
		as_dict=True,
	)

	return columns, rows
