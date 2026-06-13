# Copyright (c) 2026, Omnexa
import json, frappe
from frappe.tests.utils import FrappeTestCase
from omnexa_credit_engine.ce_gap_register import GLOBAL_LEADER_TARGET, get_gap_status
from omnexa_credit_engine.ce_global_benchmark import get_global_ce_score
from omnexa_credit_engine.workspace.ce_workspace import sync_ce_workspace_menu

class TestCeGlobalBenchmark(FrappeTestCase):
	def test_global_score(self):
		s = get_global_ce_score()
		self.assertGreaterEqual(s["weighted_score"], GLOBAL_LEADER_TARGET)
		self.assertTrue(s.get("global_leader_gate"))
	def test_gaps_closed(self):
		self.assertTrue(get_gap_status()["global_leader_gate"])
	def test_workspace_sync(self):
		stats = sync_ce_workspace_menu(save=True, rebuild=True)
		self.assertGreater(stats["total_links"], 10)
		ws = frappe.get_doc("Workspace", "Credit Engine")
		self.assertGreater(len(ws.shortcuts), 5)
