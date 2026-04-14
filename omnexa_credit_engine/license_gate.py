# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

_APP = "omnexa_credit_engine"


def before_request():
	"""Gate HTTP requests when omnexa_license_enforce is on (see omnexa_core.omnexa_license)."""
	if frappe.conf.get("omnexa_license_enforce") not in (1, True, "1", "true", "True"):
		return
	if not getattr(frappe.local, "request", None):
		return
	path = frappe.local.request.path or ""
	for prefix in ("/assets/", "/files/", "/.well-known"):
		if path.startswith(prefix):
			return
	from omnexa_core.omnexa_core.omnexa_license import assert_app_licensed_or_raise

	assert_app_licensed_or_raise(_APP)
