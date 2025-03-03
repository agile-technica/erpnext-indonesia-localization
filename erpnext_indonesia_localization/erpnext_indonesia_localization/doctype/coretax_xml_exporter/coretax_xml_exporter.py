# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from jinja2 import Environment, FileSystemLoader


class CoretaxXMLExporter(Document):
	def before_submit(self):
		self.status = "In Process"
		self.export_xml()

	@frappe.whitelist()
	def export_xml(self):
		try:
			export_xml(doc=self)

			return "Succeed"
		except Exception:
			return "Failed"


def export_xml(doc):
	invoice_docs, company_doc = fetch_sales_invoices(doc)
	validate_no_sales_invoices(doc, invoice_docs)
	tax_data = mapping_sales_invoices(invoice_docs, company_doc, doc)
	generated_xml_file(tax_data, company_doc, doc)


@frappe.whitelist()
def get_preview_sales_invoice(company, start_invoice_date, end_invoice_date, branch=None):
	filters = {
		"docstatus": 1,
		"nomor_faktur_pajak": "",
		"is_xml_generated": 0,
		"company": company,
		"posting_date": ["between", [start_invoice_date, end_invoice_date]],
	}

	if frappe.get_meta("Sales Invoice").has_field("branch") and branch:
		filters["branch"] = branch

	invoices = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=["name", "posting_date", "customer", "grand_total", "total_taxes_and_charges"]
	)

	if not invoices:
		return "<p>No sales invoices found for the selected date range</p>"

	html = """
		<table class="table table-bordered text-nowrap table-responsive">
			<tr>
				<th>No.</th>
				<th>Invoice Number</th>
				<th>Posting Date</th>
				<th>Customer</th>
				<th>Customer Name</th>
				<th>Grand Total (In Company Currency)</th>
				<th>Total Taxes and Charges (In Company Currency)</th>
			</tr>
	"""

	for idx, row in enumerate(invoices):
		company_name = frappe.get_value("Customer", row.customer, "customer_name")
		idx += 1
		if idx > 10:
			html += f"""
				<tr>
					<td colspan="7">Showing only first {idx - 1} rows out {len(invoices)}</td>
				</tr>
			"""
			break

		html += f"""
			<tr>
				<td>{idx}</td>
				<td>{row.name}</td>
				<td>{row.posting_date}</td>
				<td>{row.customer}</td>
				<td>{company_name}</td>
				<td>{"{:,.2f}".format(row.grand_total)}</td>
				<td>{"{:,.2f}".format(row.total_taxes_and_charges)}</td>
			</tr>
		"""

	html += """</table>"""

	return html


def fetch_sales_invoices(doc):
	"""
	:param doc: Object
	:return: invoices_docs, company_docs
	"""
	filters = {
		"docstatus": 1,
		"nomor_faktur_pajak": "",
		"is_xml_generated": 0,
		"company": doc.company,
		"posting_date": ["between", [doc.start_invoice_date, doc.end_invoice_date]],
	}

	if doc.branch:
		filters["branch"] = doc.branch

	invoice_docs = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=["name", "posting_date", "tax_invoice_type", "transaction_code", "tax_additional_info", "tax_custom_document", "tax_facility_stamp", "customer"]
	)

	company_doc = frappe.get_value("Company", doc.company, ["tax_id", "companys_nitku", "company_name"], as_dict=True)

	return invoice_docs, company_doc


def mapping_sales_invoices(invoice_docs, company_doc, doc):
	"""
	:param invoice_docs: List of Dictionary
	:param company_doc: Dictionary
	:param doc: Object
	:return: tax_data
	"""

	tax_data = {
		"tin": company_doc.tax_id,
		"sales_invoices": []
	}

	for invoice in invoice_docs:
		customer_info = frappe.get_value("Customer",
										 invoice["customer"],
										 ["customer_name", "customer_id_type", "passport_number", "tax_id",
										  "tax_country_code", "company_address_tax_id", "customer_email_as_per_tax_id",
										  "customers_nitku"],
										 as_dict=True)

		tax_data["sales_invoices"].append({
			"posting_date": str(invoice["posting_date"]),
			"opt": invoice["tax_invoice_type"],
			"kode_transaksi": invoice["transaction_code"],
			"additional_info": "" if invoice["tax_additional_info"] in ["", None] else invoice["tax_additional_info"],
			"custom_document": "" if invoice["tax_custom_document"] in ["", None] else invoice["tax_custom_document"],
			"name": invoice["name"],
			"facility_stamp": "" if invoice["tax_facility_stamp"] in ["", None] else invoice["tax_facility_stamp"],
			"seller_id_ntku": str(company_doc.tax_id) + str(company_doc.companys_nitku),
			"buyer_tin": customer_info.tax_id,
			"buyer_document": "" if customer_info.customer_id_type in ["", None] else customer_info.customer_id_type,
			"buyer_country_code": customer_info.tax_country_code,
			"buyer_document_number": "" if customer_info.customer_id_type in ["TIN",
																			  None] else customer_info.passport_number,
			"customer_name": customer_info.customer_name,
			"customer_address": "" if customer_info.company_address_tax_id in ["",
																			   None] else customer_info.company_address_tax_id,
			"customer_email_as_per_tax_id": "" if customer_info.customer_email_as_per_tax_id in ["",
																								 None] else customer_info.customer_email_as_per_tax_id,
			"customers_nitku": customer_info.customers_nitku,
			"items": []
		})

		frappe.db.set_value("Sales Invoice", invoice["name"], {
			"is_xml_generated": 1,
			"coretax_xml_exporter": doc.name
		})

	for sales_invoice in tax_data["sales_invoices"]:
		si_items = frappe.db.get_all(
			"Sales Invoice Item",
			filters={
				"parent": sales_invoice["name"],
				"docstatus": 1
			},
			fields=["item_name", "item_code", "qty", "uom", "rate", "discount_amount", "net_amount",
					"other_tax_base_amount", "vat_amount", "luxury_goods_tax_rate", "luxury_goods_tax_amount"]
		)

		for item in si_items:
			item_info = frappe.get_value("Item",
										 item["item_code"],
										 ["barang_jasa_opt", "barang_jasa_ref"],
										 as_dict=True)
			template_tax = frappe.get_value("Sales Taxes and Charges",
											{"parent": sales_invoice["name"], "idx": 1},
											["custom_use_temporary_rate", "rate", "custom_temporary_rate"],
											as_dict=True)

			sales_invoice["items"].append({
				"opt": item_info.barang_jasa_opt,
				"code": item_info.barang_jasa_ref,
				"name": item["item_name"],
				"unit": frappe.get_value("UOM", item["uom"], "unit_ref"),
				"price": item["rate"],
				"qty": item["qty"],
				"total_discount": item["discount_amount"] * item["qty"],
				"tax_base": item["net_amount"],
				"other_tax_base": item["other_tax_base_amount"],
				"vat": float(item["vat_amount"]),
				"vatrate": int(
					template_tax.custom_temporary_rate if template_tax.custom_use_temporary_rate else template_tax.rate),
				"stlg_rate": 0.00 if item["luxury_goods_tax_rate"] in ["", None] else float(
					item["luxury_goods_tax_rate"]),
				"stlg": 0.00 if item["luxury_goods_tax_amount"] in ["", None] else float(
					item["luxury_goods_tax_amount"])
			})

	return tax_data


def generated_xml_file(tax_data, company_doc, doc):
	"""
	:param tax_data: List of Dictionary
	:param company_doc: Dictionary
	:param doc: Object
	"""

	env = Environment(loader=FileSystemLoader("/workspace/frappe-bench/apps/erpnext_indonesia_localization/erpnext_indonesia_localization/templates"))
	template = env.get_template('tax_invoice_bulk.jinja')
	output = template.render(customer_sales_invoice_docs=tax_data)
	file_name = f"Exporter {company_doc.company_name} {doc.start_invoice_date} to {doc.end_invoice_date}.xml"
	file_path = f"/workspace/frappe-bench/sites/{frappe.local.site}/private/files/{file_name}"

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(output)

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_url": f"/private/files/{file_name}",
		"file_name": file_name,
		"attached_to_doctype": doc.doctype,
		"attached_to_name": doc.name,
	})

	file_doc.save()


def validate_no_sales_invoices(doc, invoice_docs):
	"""
	:param doc: Object
	:param invoice_docs:  List of Dictionary
	"""
	if not invoice_docs:
		frappe.msgprint(f"The company has no sales invoices from {datetime.strptime(doc.start_invoice_date, '%Y-%m-%d')}, to {datetime.strptime(doc.end_invoice_date, '%Y-%m-%d')}.")
