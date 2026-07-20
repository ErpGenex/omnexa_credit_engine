# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations


def get_standards_profile() -> dict:
	"""International standards posture for omnexa_credit_engine."""
	return {
		"app": "omnexa_credit_engine",
		"standards": ['IFRS', 'IFRS9', 'BASEL_III_IV', 'GAAP', 'ISO_27001', 'ISO_20022', 'SOX'],
		"activity_controls": ['scoring-governance', 'policy-rules', 'underwriting-audit', 'exposure-limits'],
		"multi_country_ready": True,
		"auditability": "high",
		"api_contract_version": "v1"
	}
