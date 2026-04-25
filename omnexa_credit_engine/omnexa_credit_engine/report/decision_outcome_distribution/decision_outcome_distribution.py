from __future__ import annotations

import frappe


def execute(filters=None):
	columns = [
		{"label": "Country", "fieldname": "country_code", "fieldtype": "Data", "width": 100},
		{"label": "Product", "fieldname": "product_code", "fieldtype": "Data", "width": 140},
		{"label": "Segment", "fieldname": "customer_segment", "fieldtype": "Data", "width": 140},
		{"label": "Approve", "fieldname": "approve_count", "fieldtype": "Int", "width": 90},
		{"label": "Review", "fieldname": "review_count", "fieldtype": "Int", "width": 90},
		{"label": "Decline", "fieldname": "decline_count", "fieldtype": "Int", "width": 90},
		{"label": "Total", "fieldname": "total_count", "fieldtype": "Int", "width": 90},
	]

	rows = frappe.db.sql(
		"""
		select
			ifnull(country_code, 'INTL') as country_code,
			ifnull(product_code, 'GENERIC') as product_code,
			ifnull(customer_segment, 'STANDARD') as customer_segment,
			sum(case when decision_status = 'APPROVE' then 1 else 0 end) as approve_count,
			sum(case when decision_status = 'REVIEW' then 1 else 0 end) as review_count,
			sum(case when decision_status = 'DECLINE' then 1 else 0 end) as decline_count,
			count(*) as total_count
		from `tabCredit Decision Case`
		group by country_code, product_code, customer_segment
		order by total_count desc
		""",
		as_dict=True,
	)

	return columns, rows
