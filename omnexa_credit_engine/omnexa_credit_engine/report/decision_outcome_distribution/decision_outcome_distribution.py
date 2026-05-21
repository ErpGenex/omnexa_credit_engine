# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



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
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Credit Decision Case", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			ifnull(country_code, 'INTL') as country_code,
			ifnull(product_code, 'GENERIC') as product_code,
			ifnull(customer_segment, 'STANDARD') as customer_segment,
			sum(case when decision_status = 'APPROVE' then 1 else 0 end) as approve_count,
			sum(case when decision_status = 'REVIEW' then 1 else 0 end) as review_count,
			sum(case when decision_status = 'DECLINE' then 1 else 0 end) as decline_count,
			count(*) as total_count
		FROM `tabCredit Decision Case`
		WHERE {' AND '.join(conditions)}
		GROUP BY country_code, product_code, customer_segment
		ORDER BY total_count desc
		""",
		params,
		as_dict=True,
	)
	return columns, rows
