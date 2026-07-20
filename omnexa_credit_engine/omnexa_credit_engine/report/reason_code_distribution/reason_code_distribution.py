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
	filters = prepare_filters(filters)
	filters_dict = get_all_filters(filters, "Credit Decision Case", date_field="creation", company=True, branch=True, extra_links={})
	data = frappe.get_all(
		"Credit Decision Case",
		fields=['reason_codes_json'],
		filters=filters_dict,
		limit_page_length=5000,
	)

	return [
		{"label": _("Reason Code"), "fieldname": "reason_code", "fieldtype": "Data", "width": 130},
		{"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 220},
		{"label": _("Count"), "fieldname": "count", "fieldtype": "Int", "width": 100},
	], data
