import frappe

from frappe.tests.utils import FrappeTestCase
from erpnext_indonesia_localization.utils.install import create_sales_taxes_and_charges_templates


class TestUtils(FrappeTestCase):
	def test_create_two_sales_taxes_and_charges_templates(self):
		create_sales_taxes_and_charges_templates()
