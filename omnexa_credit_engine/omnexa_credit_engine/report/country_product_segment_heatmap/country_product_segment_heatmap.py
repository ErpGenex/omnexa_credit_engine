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
		{"label": _("Country"), "fieldname": "country_code", "fieldtype": "Data", "width": 100},
		{"label": _("Product"), "fieldname": "product_code", "fieldtype": "Data", "width": 140},
		{"label": _("Segment"), "fieldname": "customer_segment", "fieldtype": "Data", "width": 140},
		{"label": _("Portfolio"), "fieldname": "portfolio_name", "fieldtype": "Data", "width": 140},
		{"label": _("Cases"), "fieldname": "cases", "fieldtype": "Int", "width": 90},
		{"label": _("Avg Score"), "fieldname": "avg_score", "fieldtype": "Float", "width": 110},
		{"label": _("Avg DTI"), "fieldname": "avg_dti", "fieldtype": "Percent", "width": 100},
		{"label": _("Avg LTV"), "fieldname": "avg_ltv", "fieldtype": "Percent", "width": 100},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Credit Decision Case", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			ifnull(country_code, 'INTL') as country_code,
			ifnull(product_code, 'GENERIC') as product_code,
			ifnull(customer_segment, 'STANDARD') as customer_segment,
			ifnull(portfolio_name, 'GLOBAL') as portfolio_name,
			count(*) as cases,
			avg(ifnull(score, 0)) as avg_score,
			avg(ifnull(dti, 0)) as avg_dti,
			avg(ifnull(ltv, 0)) as avg_ltv
		FROM `tabCredit Decision Case`
		WHERE {' AND '.join(conditions)}
		GROUP BY country_code, product_code, customer_segment, portfolio_name
		ORDER BY cases desc
		""",
		params,
		as_dict=True,
	)
	return columns, rows
