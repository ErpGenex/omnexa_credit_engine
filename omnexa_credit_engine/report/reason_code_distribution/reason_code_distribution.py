from __future__ import annotations

import json
from collections import Counter

import frappe


def execute(filters=None):
	columns = [
		{"label": "Reason Code", "fieldname": "reason_code", "fieldtype": "Data", "width": 130},
		{"label": "Title", "fieldname": "title", "fieldtype": "Data", "width": 220},
		{"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 100},
	]

	rows = frappe.get_all("Credit Decision Case", fields=["reason_codes_json"])
	counter: Counter[str] = Counter()
	title_map: dict[str, str] = {}
	for row in rows:
		try:
			reason_codes = json.loads(row.reason_codes_json or "[]")
		except Exception:
			reason_codes = []
		for reason in reason_codes:
			code = reason.get("code")
			if not code:
				continue
			counter[code] += 1
			title_map[code] = reason.get("title", "")

	data = [
		{"reason_code": code, "title": title_map.get(code, ""), "count": count}
		for code, count in counter.most_common()
	]
	return columns, data
