# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from indonesia_taxes_and_charges.utils.data import get_tax_prefix_code


class TaxInvoiceNumber(Document):
	def rollback_tin_to_available(self, si_doc):
		self.tax_invoice_number = self.name
		self.status = "Available"
		self.linked_si = None
		self.linked_datetime = None

		self.save(ignore_permissions=True, ignore_version=True)


@frappe.whitelist()
def unlink_tax_invoice_number(tax_invoice_number):
	tin_doc = frappe.get_doc("Tax Invoice Number", tax_invoice_number)
	si_doc = frappe.get_doc("Sales Invoice", tin_doc.linked_si)
	tin_doc.rollback_tin_to_available(si_doc)

	tin_exporter_item = frappe.db.exists("Tax Invoice Exporter Item", {
		"sales_invoice": si_doc.name
	})
	frappe.db.set_value(
		"Tax Invoice Exporter Item",
		tin_exporter_item,
		'is_tin_unlinked_from_invoice',
		True,
		update_modified=False
	)
	frappe.db.set_value('Sales Invoice', si_doc.name, 'tax_invoice_number', None, update_modified=False)
