# -*- coding: utf-8 -*-
# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import csv
import re
import os

import frappe

from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_datetime
from frappe.utils.background_jobs import enqueue
from frappe.exceptions import QueryDeadlockError
import time


import erpnext_indonesia_localization.utils.constants as constants

from erpnext_indonesia_localization.utils.data import cint, get_tax_prefix_code
from frappe.utils import floor, ceil, flt, cstr


class TaxInvoiceExporter(Document):
	def validate(self):
		for si in self.sales_invoices:
			if frappe.db.sql("""
				SELECT name
				FROM `tabTax Invoice Exporter Item`
				WHERE sales_invoice = %s
				AND parent != %s
				AND docstatus != 2
			""", (si.sales_invoice, self.name)):
				frappe.throw(si.sales_invoice + _(" already has Tax Invoice Number"))

	def before_submit(self):
		self.validate_used_tin()

	def on_submit(self):
		self.update_tin_with_si("on_submit")

	def on_cancel(self):
		self.update_tin_with_si("before_cancel")

	def validate_used_tin(self):
		used_tin = ""
		for invoice_row in self.sales_invoices:
			tin_exporter_invoice = frappe.get_all("Tax Invoice Exporter Item", filters={
				"tax_invoice_number": invoice_row.tax_invoice_number,
				"parent": ["!=", self.name],
				"is_invoice_cancelled": 0,
				"docstatus": ["!=", 2]
			}, fields=["tax_invoice_number"], parent_doctype="Tax Invoice Exporter")

			for tin_exporter_row in tin_exporter_invoice:
				if tin_exporter_row.tax_invoice_number not in used_tin:
					used_tin += tin_exporter_row.tax_invoice_number if used_tin == "" else (
							", " + tin_exporter_row.tax_invoice_number)

		if used_tin:
			error_msg = _(f"Tax Invoice Number {used_tin} is already used in other existing Tax Invoice Exporter. ")
			error_msg += _("Please click the Get Sales Invoice button again to replace the number")

			frappe.throw(error_msg)

	@frappe.whitelist()
	def update_tin_with_si(self, event_trigger):
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")

		if "submit" in event_trigger:
			list_of_tin = []
			last_entry_si_row = self.sales_invoices[-1]

			queue_name = "long"
			if indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job:
				queue_name = indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job

			for tie_si in self.sales_invoices:
				si_doc = frappe.get_doc("Sales Invoice", tie_si.sales_invoice)
				prefix_code = get_tax_prefix_code(si_doc)
				if self.assign_tax_invoice_number_to_multiple_invoices:
					invoices_per_tin = []

					if tie_si.tax_invoice_number not in list_of_tin:
						list_of_tin.append(tie_si.tax_invoice_number)
						formatted_tin = tie_si.tax_invoice_number

						for invoice_row in self.sales_invoices:
							if invoice_row.tax_invoice_number == tie_si.tax_invoice_number:
								invoices_per_tin.append(frappe._dict({
									"sales_invoice_id": invoice_row.sales_invoice,
									"is_invoice_cancelled": 0 if si_doc.docstatus == 1 else 1
								}))

						enqueue(
							job_name=(f"Updating Tax Invoice Number on {self.name}"),
							queue=indonesia_localization_settings.worker_for_renaming_tax_invoice_number if indonesia_localization_settings.worker_for_renaming_tax_invoice_number else "short",
							is_async=True,
							method=self.update_tin_doc,
							tin_doc_name=tie_si.tax_invoice_number,
							values={
								"tin_name": prefix_code + "." + formatted_tin,
								"tin": prefix_code + "." + tie_si.tax_invoice_number,
								"linked_si": invoices_per_tin[0].sales_invoice_id if len(
									invoices_per_tin) == 1 else None,
								"linked_datetime": get_datetime(),
								"tin_status": "Used",
								"list_of_sales_invoice": invoices_per_tin if len(invoices_per_tin) > 1 else None
							}
						)

					frappe.db.set_value(
						'Sales Invoice', si_doc.name, 'tax_invoice_number',
						prefix_code + "." + formatted_tin, update_modified=False
					)
				else:
					if indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job:
						frappe.db.set_value(
							'Sales Invoice', si_doc.name, 'linking_sales_invoice_to_tax_invoice_number',
							1, update_modified=False
						)

					enqueue(
						job_name=("Linking TIN to SI " + si_doc.name),
						queue=queue_name,
						is_async=True,
						method=self.set_tin_to_si,
						si_row=tie_si,
						prefix_code=prefix_code,
						last_entry_row=last_entry_si_row
					)

		else:
			indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")

			queue_name = "short"
			if indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job:
				queue_name = indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job

			enqueue(
				job_name=f"update_tin_with_si | Removing TIN from TIE {self.name}",
				queue=queue_name,
				is_async=True,
				method=self.remove_tin_from_si
			)

	def set_tin_to_si(self, si_row, prefix_code, last_entry_row):

		max_retries = 5
		retry_delay = 1

		for _ in range(max_retries):
			try:
				formatted_tin = si_row.tax_invoice_number

				formatted_tin_w_prefix_code = prefix_code + "." + formatted_tin
				# enqueue(
				# 	job_name=("Set SI to TIN " + formatted_tin),
				# 	queue="long",
				# 	is_async=True,
				# 	method=self.update_tin_doc,
				# 	tin_doc_name=si_row.tax_invoice_number,
				# 	values={
				# 		"tin_name": formatted_tin_w_prefix_code,
				# 		"tin": prefix_code + "." + si_row.tax_invoice_number,
				# 		"linked_si": si_row.sales_invoice,
				# 		"linked_datetime": get_datetime(),
				# 		"tin_status": "Used"
				# 	}
				# )
				self.update_tin_doc(si_row.tax_invoice_number, values={
					"tin_name": formatted_tin_w_prefix_code,
					"tin": prefix_code + "." + si_row.tax_invoice_number,
					"linked_si": si_row.sales_invoice,
					"linked_datetime": get_datetime(),
					"tin_status": "Used"
				})

				frappe.db.set_value(
					'Sales Invoice', si_row.sales_invoice, 'tax_invoice_number', formatted_tin_w_prefix_code
				)

				if si_row.sales_invoice == last_entry_row.sales_invoice:
					frappe.db.set_value(
						self.doctype, self.name, 'linking_tin_to_si_status', "TIN Successfully linked to SI"
					)
					frappe.db.commit()

				break
			except QueryDeadlockError:
				frappe.db.rollback()
				time.sleep(retry_delay)

		else:
			pass

	def remove_tin_from_si(self):
		for si in self.sales_invoices:
			si_doc = frappe.get_doc("Sales Invoice", si.sales_invoice)
			tin_doc = frappe.get_doc("Tax Invoice Number", si.tax_invoice_number)

			prefix_code = get_tax_prefix_code(si_doc)

			frappe.db.set_value('Sales Invoice', si_doc.name, 'tax_invoice_number', None, update_modified=False)

			tin_wo_prefix = tin_doc.name.lstrip(prefix_code).lstrip(".")

			self.update_tin_doc(tin_doc.name, values={
				"tin_name": tin_wo_prefix,
				# "tin": tin_wo_prefix.replace(".", ""),
				"tin": tin_wo_prefix,
				"linked_si": None,
				"linked_datetime": None,
				"tin_status": "Available"
			})

		self.reload()

	def update_tin_doc(self, tin_doc_name, values, rename=True):

		frappe.db.sql(
			"""
			UPDATE `tabTax Invoice Number`
			SET
				`tax_invoice_number` = %(tin)s,
				`linked_datetime` = %(linked_datetime)s,
				`status` = %(tin_status)s,
				`linked_si` = %(linked_si)s
			WHERE
				`name` = %(tin_doc_name)s;
			""",
			{
				"tin": values.get("tin"),
				"linked_datetime": values.get("linked_datetime"),
				"tin_status": values.get("tin_status"),
				"linked_si": values.get("linked_si"),
				"tin_doc_name": tin_doc_name
			}
		)

		if values.get("list_of_sales_invoice"):
			frappe.db.sql(
				"""
				INSERT INTO `tabList of Sales Invoice` (`parent`, `parentfield`, `parenttype`, `list_of_sales_invoice`)
				VALUES (%(parent)s, %(parentfield)s, %(parenttype)s, %(list_of_sales_invoice)s);
				""",
				{
					"parents": tin_doc_name,
					"parentfield": "list_of_sales_invoice",
					"parenttype": "Tax Invoice Number",
					"list_of_sales_invoice": values.get("list_of_sales_invoice")
				}
			)

		# Commit the changes to the database
		frappe.db.commit()

	# if rename:
	# 	frappe.rename_doc("Tax Invoice Number", tin_doc.name, values.get("tin_name"))

	def validate_field_value(self):
		if not self.company:
			frappe.throw(_("Please fill field Company"))
		elif not self.start_sales_invoice_posting_date:
			frappe.throw(_("Please fill field Start Sales Invoice Posting Date"))
		elif not self.end_sales_invoice_posting_date:
			frappe.throw(_("Please fill field End Sales Invoice Posting Date"))
		elif not self.company and not (self.start_sales_invoice_posting_date or self.end_sales_invoice_posting_date):
			frappe.throw(_("Please fill field Company and Sales Invoice Posting Date (Start and End)"))

	def get_si_without_tin(self):
		fields = ["name", "customer", "customer_name", "posting_date", "grand_total", "amended_from"]
		filters = [
			['name', 'not in', self.get_si_in_table()],
			['posting_date', 'between', [self.start_sales_invoice_posting_date, self.end_sales_invoice_posting_date]],
			['tax_id', 'is', 'set'],
			['tax_invoice_number', 'is', 'not set'],
			['company', '=', self.company],
			['status', 'in', [
				'Submitted',
				'Paid',
				'Partly Paid',
				'Unpaid',
				'Unpaid and Discounted',
				'Partly Paid and Discounted',
				'Overdue and Discounted',
				'Overdue'
			]],
			['docstatus', '=', 1],
			["customer", "in", self.get_customer()],
			["taxes_and_charges", "is", "set"]
		]

		indonesia_localization_settings_doc = frappe.get_single("Indonesia Localization Settings")

		if indonesia_localization_settings_doc.exclude_opening_entry:
			filters.append(["is_opening", "=", "No"])

		if self.branch and frappe.db.exists("Branch", self.branch):
			filters.append(["branch", "=", self.branch])
			fields.append("branch")

		if indonesia_localization_settings_doc.exclude_sales_invoice_type_return:
			filters.append(["is_return", "=", 0])

		return frappe.get_list("Sales Invoice", filters=filters, fields=fields)

	def get_customer(self):
		if self.customer_type == "All":
			return frappe.get_all("Customer", pluck="name")
		elif self.customer_type == "PKP":
			return frappe.get_all("Customer", filters={
				"customer_pkp": 1
			}, pluck="name")
		else:
			return frappe.get_all("Customer", filters={
				"customer_pkp": 0
			}, pluck="name")

	def get_si_in_table(self):
		return frappe.get_all("Tax Invoice Exporter Item", filters=[
			["docstatus", "=", 0],
			["parent", "!=", self.name]
		], fields=["sales_invoice"], pluck="sales_invoice")

	def get_available_tin(self, limit):
		tin_exporter_invoice = frappe.get_all("Tax Invoice Exporter Item", fields=["tax_invoice_number"],
											  filters={"docstatus": ["!=", 2]}, parent_doctype="Tax Invoice Exporter",
											  pluck="tax_invoice_number")

		return frappe.get_all("Tax Invoice Number", filters=[
			['status', '=', 'Available'],
			['company', '=', self.company],
			["name", "not in", tin_exporter_invoice]
		], fields=[
			"name"
		], order_by='tax_invoice_number asc', limit=limit)

	@frappe.whitelist()
	def fill_sales_invoices(self, is_single_tax_invoice_number):
		self.validate_field_value()
		frappe.db.set_value(self.doctype, self.name, 'is_loading_filling_si', 1)

		si_without_tin = self.get_si_without_tin()
		available_tin = self.get_available_tin(limit=len(si_without_tin))

		if not si_without_tin:
			frappe.throw(_("No Sales Invoice can be processed"))

		if len(available_tin) >= len(si_without_tin):
			generated_si = self.generate_si_detail(is_single_tax_invoice_number, si_without_tin, available_tin)

			return generated_si
		else:
			frappe.throw(_("Insufficient Tax Invoice Number"))

	def generate_si_detail(self, is_single_tax_invoice_number, si_without_tin, available_tin, is_auto_draft_enabled=False):
		si_details = []

		if not is_single_tax_invoice_number:
			for index, si in enumerate(si_without_tin):
				dn_list = self.get_delivery_note(si.get('name'))

				si_details.append({
					"sales_invoice": si.get('name'),
					"delivery_note": ", ".join(dn_list) if dn_list else None,
					"tax_invoice_number": self.get_tin_for_si(available_tin, index, si),
					"total_amount": si.get('grand_total'),
					"sales_invoice_date": si.get('posting_date'),
					"customer": si.get('customer'),
					"customer_name": si.get('customer_name'),
					"branch": si.get("branch")
				})
		else:
			tax_invoice_number = {}

			for index, si in enumerate(si_without_tin):
				dn_list = self.get_delivery_note(si.get('name'))

				if si.customer not in tax_invoice_number:
					tax_invoice_number.update({
						si.customer: self.get_tin_for_si(available_tin, index, si)
					})

				si_details.append({
					"sales_invoice": si.get('name'),
					"delivery_note": ", ".join(dn_list),
					"total_amount": si.get('grand_total'),
					"sales_invoice_date": si.get('posting_date'),
					"customer": si.get('customer'),
					"customer_name": si.get('customer_name'),
					"branch": si.get("branch"),
					"tax_invoice_number": tax_invoice_number[si.customer]
				})

		if is_auto_draft_enabled:
			for sales_invoice in si_details:
				self.append("sales_invoices", sales_invoice)

			self.is_loading_filling_si = 0
			self.save(True)

			frappe.db.commit()
		else:
			return si_details

	@staticmethod
	def get_delivery_note(si):
		dn_list = []
		si_doc = frappe.get_doc("Sales Invoice", si)

		for item in si_doc.items:
			if item.delivery_note and item.delivery_note not in dn_list:
				dn_list.append(item.delivery_note)

		return dn_list

	@staticmethod
	def get_tin_for_si(available_tin, idx, si):
		prev_tin = frappe.get_value("Sales Invoice", si.amended_from, "tax_invoice_number")

		if si.amended_from and prev_tin:
			return prev_tin[4:]
		else:
			return available_tin[idx].get('name')

	@staticmethod
	def validate_customer_tax_detail(customer_id):
		customer_id_link = '<a href="/app/{0}/{1}">{1}</a>'.format(
			"customer",
			customer_id.name
		)

		if customer_id.customer_pkp:
			if not customer_id.tax_id:
				frappe.throw(_("Please set Tax ID field for ") + customer_id_link)

			if not customer_id.company_address_tax_id:
				frappe.throw(_("Please set Company Address as per Tax ID field for ") + customer_id_link)

			if not customer_id.company_name_tax_id:
				frappe.throw(_("Please set Company Name as per Tax ID field for ") + customer_id_link)
		else:
			if not customer_id.nik:
				frappe.throw(_("Please set NIK field for ") + customer_id_link)

	@frappe.whitelist()
	def enqueue_export_as_csv(self):
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")

		queue_name = "short"
		if indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job:
			queue_name = indonesia_localization_settings.worker_for_link_tax_invoice_number_background_job

		enqueue(
			job_name=f"enqueue_export_as_csv | Exporting TIE {self.name} to CSV",
			queue=queue_name,
			is_async=True,
			method=self.export_as_csv
		)

	def export_as_csv(self):
		try:
			generated_csv_file = open(f"{frappe.utils.get_site_path()}/private/files/{self.name}.csv", 'w', newline='')

			writer = csv.writer(generated_csv_file)

			writer.writerow(constants.HEADER_ROW_1)
			writer.writerow(constants.HEADER_ROW_2)
			writer.writerow(constants.HEADER_ROW_3)

			if self.customer_type == "Non PKP":
				self.process_csv_row_non_pkp(writer=writer)
			else:
				for si_row in self.sales_invoices:
					if not si_row.is_invoice_cancelled or not si_row.is_tin_unlinked_from_invoice:
						self.process_csv_row(si_row, writer)

			generated_csv_file.close()

			attach_csv = frappe.get_doc({
				"doctype": "File",
				"file_name": f"{self.name}.csv",
				"file_url": f"/private/files/{self.name}.csv",
				"file_size": os.path.getsize(f"{frappe.utils.get_site_path()}/private/files/{self.name}.csv"),
				"attached_to_doctype": self.doctype,
				"attached_to_name": self.name,
			})

			attach_csv.insert()

		except Exception as error:
			frappe.throw(error)

	def process_csv_row_non_pkp(self, writer):
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		customer_tax = []

		for invoice_row in self.sales_invoices:
			if not invoice_row.is_invoice_cancelled or not invoice_row.is_tin_unlinked_from_invoice:
				si_doc = frappe.get_doc("Sales Invoice", invoice_row.sales_invoice)

				if invoice_row.customer not in customer_tax:
					customer_tax.append(invoice_row.customer)

					prefix_code = get_tax_prefix_code(si_doc)
					tin_doc = frappe.get_doc("Tax Invoice Number", invoice_row.tax_invoice_number)
					cust_doc = frappe.get_doc("Customer", invoice_row.customer)

					self.validate_customer_tax_detail(cust_doc)

					customer_address = cstr(cust_doc.company_address_tax_id)

					customer_address = customer_address.replace("\n", "").replace('<br>', ',').rstrip(',')

					formatted_posting_date = '{0}/{1}/{2}'.format(
						si_doc.posting_date.day, si_doc.posting_date.month, si_doc.posting_date.year
					)

					if indonesia_localization_settings.invoice_name_in_efaktur_template:
						invoice_name = si_doc.as_dict()[indonesia_localization_settings.invoice_name_in_efaktur_template]
					else:
						invoice_name = si_doc.name

					name_tax_id = cust_doc.customer_name
					name_tax_invoice_number = None

					if indonesia_localization_settings.no_faktur_format == 0:
						name_tax_invoice_number = tin_doc.tax_invoice_number.replace(".", "")[-13:]
					else:
						name_tax_invoice_number = tin_doc.tax_invoice_number[-13:-10] + '.' + tin_doc.tax_invoice_number[-10:-8] + '.' + tin_doc.tax_invoice_number[-8:]

					tax_additional_description = 0
					if si_doc.tax_additional_description:
						tax_additional_description = si_doc.tax_additional_description

					writer.writerow([
						'FK', prefix_code[:2], prefix_code[2:3],
						name_tax_invoice_number,
						si_doc.posting_date.month, si_doc.posting_date.year, formatted_posting_date,
						cust_doc.nik, name_tax_id, customer_address,
						floor(total), floor(total_taxes_and_charges),
						0, tax_additional_description, 0, 0, 0, 0, invoice_name, ''
					])

					self.process_per_invoice_item_to_csv(customer=invoice_row.customer, writer=writer)

	def process_per_invoice_item_to_csv(self, customer, writer):
		for invoice_row in self.sales_invoices:
			if invoice_row.customer == customer:
				si_doc = frappe.get_doc("Sales Invoice", invoice_row.sales_invoice)

				total_base_net_amount = 0
				total_taxes_and_charges = 0
				tax_rate = si_doc.taxes[0].rate / 100

				for idx, item in enumerate(si_doc.items):
					total_base_net_amount += floor(item.base_net_amount)
					total_taxes_and_charges += floor(floor(item.base_net_amount) * tax_rate)

					rate_before_discount = cint(item.net_rate) + cint(item.discount_amount)

					if idx + 1 == len(si_doc.items):
						total_base_net_amount_diff = total_base_net_amount - floor(si_doc.total)
						total_taxes_and_charges_diff = total_taxes_and_charges - floor(si_doc.total_taxes_and_charges)
					else:
						total_base_net_amount_diff = 0
						total_taxes_and_charges_diff = 0

					writer.writerow([
						'OF', '', item.item_name, rate_before_discount, cint(item.qty),
						rate_before_discount * cint(item.qty),
						flt(item.discount_amount) * cint(item.qty),
						floor(item.base_net_amount) - total_base_net_amount_diff,
						floor(floor(item.base_net_amount) * tax_rate) - total_taxes_and_charges_diff, 0, 0
					])

	def generate_invoice_name_for_cust_non_pkp(self, customer):
		invoice_name = ""
		total = 0
		total_taxes_and_charges = 0

		for invoice_row in self.sales_invoices:
			if invoice_row.customer == customer:
				si_doc = frappe.get_doc("Sales Invoice", invoice_row.sales_invoice)
				tax_additional_reference = ""
				if si_doc.tax_additional_reference:
					tax_additional_reference = f" Dokumen Referensi {si_doc.tax_additional_reference}"

				for item_row in si_doc.items:
					if invoice_name == "":
						invoice_name += f"{item_row.delivery_note},{invoice_row.sales_invoice}"
					else:
						invoice_name += ", " + f"{item_row.delivery_note}/{invoice_row.sales_invoice}{tax_additional_reference}"

					break

				total += floor(si_doc.total)
				total_taxes_and_charges += floor(si_doc.total_taxes_and_charges)

		return invoice_name, total, total_taxes_and_charges

	def process_csv_row(self, si_row, writer):
		indonesia_localization_settings = frappe.get_single("Indonesia Localization Settings")
		si_doc = frappe.get_doc("Sales Invoice", si_row.sales_invoice)
		tin_doc = frappe.get_doc("Tax Invoice Number", si_row.tax_invoice_number)
		cust_doc = frappe.get_doc("Customer", si_doc.customer)

		self.validate_customer_tax_detail(cust_doc)

		total_base_net_amount = 0
		total_taxes_and_charges = 0
		tax_rate = si_doc.taxes[0].rate / 100
		prefix_code = get_tax_prefix_code(si_doc)
		unformatted_tax_id = re.sub('[^A-Za-z0-9]+', '', cust_doc.tax_id)

		formatted_posting_date = '{0}/{1}/{2}'.format(
			si_doc.posting_date.day, si_doc.posting_date.month, si_doc.posting_date.year
		)

		if cust_doc.company_address_tax_id:
			customer_address = cstr(cust_doc.company_address_tax_id)
		else:
			customer_address = 'N/A'

		si_item_row = []

		for idx, item in enumerate(si_doc.items):
			# write row for every item in sales invoice
			total_base_net_amount += floor(item.base_net_amount)
			total_taxes_and_charges += floor(floor(item.base_net_amount) * tax_rate)

			rate_before_discount = cint(item.net_rate) + cint(item.discount_amount)

			if idx + 1 == len(si_doc.items):
				total_base_net_amount_diff = total_base_net_amount - floor(si_doc.total)
				total_taxes_and_charges_diff = total_taxes_and_charges - floor(si_doc.total_taxes_and_charges)
			else:
				total_base_net_amount_diff = 0
				total_taxes_and_charges_diff = 0

			si_item_row.append([
				'OF', '', item.item_name, rate_before_discount, cint(item.qty),
				rate_before_discount * cint(item.qty),
				flt(item.discount_amount) * cint(item.qty),
				floor(item.base_net_amount) - total_base_net_amount_diff,
				floor(floor(item.base_net_amount) * tax_rate) - total_taxes_and_charges_diff, 0, 0
			])

		if indonesia_localization_settings.invoice_name_in_efaktur_template:
			invoice_name = si_doc.as_dict()[indonesia_localization_settings.invoice_name_in_efaktur_template]
		else:
			invoice_name = si_doc.name

		name_tax_invoice_number = None

		if indonesia_localization_settings.no_faktur_format == 0:
			name_tax_invoice_number = tin_doc.tax_invoice_number.replace(".", "")[-13:]
		else:
			name_tax_invoice_number = tin_doc.tax_invoice_number[-13:-10] + '.' + tin_doc.tax_invoice_number[-10:-8] + '.' + tin_doc.tax_invoice_number[-8:]

		tax_additional_description = 0
		if si_doc.tax_additional_description:
			tax_additional_description = si_doc.tax_additional_description

		writer.writerow([
			'FK', prefix_code[:2], prefix_code[2:3],
			name_tax_invoice_number,
			si_doc.posting_date.month, si_doc.posting_date.year, formatted_posting_date,
			unformatted_tax_id, cust_doc.company_name_tax_id, customer_address,
			floor(si_doc.total), floor(si_doc.total_taxes_and_charges),
			0, tax_additional_description, 0, 0, 0, 0, invoice_name, ''
		])

		writer.writerows(si_item_row)
