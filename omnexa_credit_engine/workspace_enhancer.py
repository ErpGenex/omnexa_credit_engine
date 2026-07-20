# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe

_APP = "omnexa_credit_engine"


def after_migrate():
	try:
		from omnexa_core.omnexa_core.workspace_control_tower import sync_workspace_for_app

		sync_workspace_for_app(_APP)
	except Exception:
		frappe.log_error(frappe.get_traceback(), f"{_APP}: workspace_control_tower")
