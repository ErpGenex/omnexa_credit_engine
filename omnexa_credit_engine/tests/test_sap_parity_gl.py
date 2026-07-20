# Copyright (c) 2026, ErpGenEx
from frappe.tests.utils import FrappeTestCase

from omnexa_finance_engine.fs_parity_bridge import preview_gl_for_vertical


class TestSapParityGl(FrappeTestCase):
	def test_preview_gl_posting_bridge(self):
		out = preview_gl_for_vertical("credit_engine", principal="1000")
		self.assertEqual(out["vertical"], "credit_engine")
		self.assertGreaterEqual(len(out["lines"]), 2)
