from __future__ import annotations

import frappe


def execute(filters=None):
	columns = [
		{"label": "Country", "fieldname": "country_code", "fieldtype": "Data", "width": 100},
		{"label": "Product", "fieldname": "product_code", "fieldtype": "Data", "width": 140},
		{"label": "Segment", "fieldname": "customer_segment", "fieldtype": "Data", "width": 140},
		{"label": "Portfolio", "fieldname": "portfolio_name", "fieldtype": "Data", "width": 140},
		{"label": "Cases", "fieldname": "cases", "fieldtype": "Int", "width": 90},
		{"label": "Avg Score", "fieldname": "avg_score", "fieldtype": "Float", "width": 110},
		{"label": "Avg DTI", "fieldname": "avg_dti", "fieldtype": "Percent", "width": 100},
		{"label": "Avg LTV", "fieldname": "avg_ltv", "fieldtype": "Percent", "width": 100},
	]

	rows = frappe.db.sql(
		"""
		select
			ifnull(country_code, 'INTL') as country_code,
			ifnull(product_code, 'GENERIC') as product_code,
			ifnull(customer_segment, 'STANDARD') as customer_segment,
			ifnull(portfolio_name, 'GLOBAL') as portfolio_name,
			count(*) as cases,
			avg(ifnull(score, 0)) as avg_score,
			avg(ifnull(dti, 0)) as avg_dti,
			avg(ifnull(ltv, 0)) as avg_ltv
		from `tabCredit Decision Case`
		group by country_code, product_code, customer_segment, portfolio_name
		order by cases desc
		""",
		as_dict=True,
	)
	return columns, rows
