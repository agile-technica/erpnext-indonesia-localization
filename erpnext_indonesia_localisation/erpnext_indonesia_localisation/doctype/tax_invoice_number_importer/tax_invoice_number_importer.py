# -*- coding: utf-8 -*-
# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils.background_jobs import enqueue

class TaxInvoiceNumberImporter(Document):
	@frappe.whitelist()
	def insert_tax_invoice_number(self):
		frappe.enqueue(
			queue="long",
			timeout="3600",
			is_async=True,
			method=self.process_tax_invoice_number
		)

	def process_tax_invoice_number(self):
		self.validate_tax_invoice_number_fields()

		tax_invoice_numbers = list(range(int(self.from_tax_invoice_number), int(self.to_tax_invoice_number) + 1))

		for tin in tax_invoice_numbers:
			tin = str(tin).zfill(13)

			tin_doc = frappe.new_doc("Tax Invoice Number")

			tin_doc.tax_invoice_number = tin
			tin_doc.tax_invoice_number_formatted = tin[:3] + "." + tin[3:5] + "." + tin[5:]
			tin_doc.status = 'Available'
			tin_doc.company = self.company
			tin_doc.creation_datetime = now()

			try:
				tin_doc.insert()
				frappe.db.commit()
			except frappe.exceptions.DuplicateEntryError as error:
				error_msg = _("Tax Invoice Number between {0} and {1} exists, ").format(
					self.from_tax_invoice_number,
					self.to_tax_invoice_number
				)
				error_msg += _("please make sure that From and To Tax Invoice Number are correct.")

				frappe.log_error(
					message=str(f"{error}\n\n{frappe.get_traceback()}\n\nuser:{frappe.session.user}"),
					title=error_msg
				)

	def validate_tax_invoice_number_fields(self):
		indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")

		if not self.from_tax_invoice_number or not self.from_tax_invoice_number_formatted \
				or not self.to_tax_invoice_number or not self.to_tax_invoice_number_formatted:
			error_msg = _("Please complete filling in Tax Invoice Number fields")

			frappe.throw(error_msg)

		if len(self.from_tax_invoice_number) != indonesia_localisation_settings.tin_length or len(
				self.to_tax_invoice_number) != indonesia_localisation_settings.tin_length:
			frappe.throw(_("Tax Invoice Number cannot be less than ") + str(indonesia_localisation_settings.tin_length) + _(
				" digits"))

		if self.from_tax_invoice_number > self.to_tax_invoice_number:
			frappe.throw("To Tax Invoice Number cannot be smaller than From Tax Invoice Number")
