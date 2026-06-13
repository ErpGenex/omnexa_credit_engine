# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe
from frappe.utils import today


def process_daily_portfolio_snapshots():
	"""Finance vertical scheduler hook — portfolio health refresh marker."""
	frappe.publish_realtime("finance_portfolio_tick", {"date": today()}, user=frappe.session.user)
