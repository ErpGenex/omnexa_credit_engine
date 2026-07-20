from frappe.tests.utils import FrappeTestCase

from omnexa_credit_engine import hooks, license_gate


class TestCreditEngineLicenseSmoke(FrappeTestCase):
	def test_license_gate_is_wired(self):
		self.assertEqual(hooks.before_request, ["omnexa_credit_engine.license_gate.before_request"])
		self.assertEqual(license_gate._APP, "omnexa_credit_engine")
