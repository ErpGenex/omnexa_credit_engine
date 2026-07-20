# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	columns = [
		{"label": _("Decision"), "fieldname": "decision_status", "fieldtype": "Data", "width": 130
	},
		{"label": _("Cases"), "fieldname": "cases", "fieldtype": "Int", "width": 100
	},
		{"label": _("Avg Latency (ms)"), "fieldname": "avg_latency_ms", "fieldtype": "Float", "width": 140
	},
		{"label": _("Max Latency (ms)"), "fieldname": "max_latency_ms", "fieldtype": "Int", "width": 140
	},
		{"label": _("SLA Breaches (>200ms)"), "fieldname": "sla_breaches", "fieldtype": "Int", "width": 170
	},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Credit Decision Case", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			ifnull(decision_status, 'UNKNOWN') as decision_status,
			count(*) as cases,
			avg(ifnull(latency_ms, 0)) as avg_latency_ms,
			max(ifnull(latency_ms, 0)) as max_latency_ms,
			sum(case when ifnull(latency_ms, 0) > 200 then 1 else 0 end) as sla_breaches
		FROM `tabCredit Decision Case`
		WHERE {' AND '.join(conditions)}
		GROUP BY decision_status
		ORDER BY cases desc
		""",
		params,
		as_dict=True,
	)
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart