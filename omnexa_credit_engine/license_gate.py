# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

_APP = "omnexa_credit_engine"


def before_request():
	"""
	Gate only this app's own API namespace.
	Global/doctype-aware enforcement is handled by omnexa_core.omnexa_core.license_gate.
	"""
	if frappe.conf.get("omnexa_license_enforce") not in (1, True, "1", "true", "True"):
		return
	if not getattr(frappe.local, "request", None):
		return
	path = frappe.local.request.path or ""
	for prefix in ("/assets/", "/files/", "/.well-known", "/api/resource/"):
		if path.startswith(prefix):
			return

	# Only enforce for /api/method/omnexa_credit_engine.*
	if not path.startswith("/api/method/"):
		return
	method = path[len("/api/method/") :].split("?", 1)[0].strip("/")
	if not method.startswith(f"{_APP}."):
		return
	from omnexa_core.omnexa_core.omnexa_license import assert_app_licensed_or_raise

	assert_app_licensed_or_raise(_APP)
