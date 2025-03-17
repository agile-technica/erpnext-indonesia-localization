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

	def before_cancel(self):
		sales_invoices = frappe.get_all("Sales Invoice", {"coretax_xml_exporter": self.name}, pluck="name")

		if len(sales_invoices) <= 500:
			unlink_sales_invoices(self.name)

		else:
			frappe.enqueue(
				method=unlink_sales_invoices,
				queue="long",
				doc_name=self.name
			)

	@frappe.whitelist()
	def export_xml(self):
		invoice_docs, company_doc = fetch_sales_invoices(doc=self)
		if len(invoice_docs) <= 500:
			result =  export_xml(invoice_docs, company_doc, doc=self)
			if result == "Failed":
				self.status = result
				frappe.throw(msg="Exporting XML Failed")
			else :
				self.status = result

				return result

		else:
			frappe.enqueue(
				method=export_xml,
				queue="long",
				invoice_docs=invoice_docs,
				company_doc=company_doc,
				doc=self
			)


def export_xml(invoice_docs, company_doc, doc):
	try:
		tax_data = mapping_sales_invoices(invoice_docs, company_doc, doc)
		generated_xml_file(tax_data, company_doc, doc)
		frappe.set_value("Coretax XML Exporter", doc.name, "status", "Succeed")

		return "Succeed"

	except Exception:
		frappe.set_value("Coretax XML Exporter", doc.name, "status", "Failed")
		frappe.log_error(title=f"CoreTax XML Exporter Error on {doc.name}", message=frappe.get_traceback())

		return "Failed"


@frappe.whitelist()
def get_preview_sales_invoice(company, start_invoice_date, end_invoice_date, branch=None):
	filters = {
		"docstatus": 1,
		"nomor_faktur_pajak": "",
		"is_xml_generated": 0,
		"company": company,
		"posting_date": ["between", [start_invoice_date, end_invoice_date]],
		"taxes_and_charges": ["!=", ""]
	}

	if branch:
		filters["branch"] = branch

	invoices = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=["name", "posting_date", "customer", "grand_total", "total_taxes_and_charges"],
		order_by='posting_date'
	)

	if not invoices:
		return "<p>No sales invoices found for the selected date range</p>"

	html = """
		<h3>Preview</h3>
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

	html += f"""
		</table>
		<h5>Showing {min(10, len(invoices))} out of {len(invoices)} row(s).</h5>
	"""

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
		"taxes_and_charges": ["!=", ""]
	}

	if doc.branch:
		filters["branch"] = doc.branch

	invoice_docs = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=["name", "posting_date", "tax_invoice_type", "transaction_code", "tax_additional_info", "tax_custom_document", "tax_facility_stamp", "customer"],
		order_by='posting_date'
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
										 ["customer_name", "customer_id_type", "customer_id_number", "tax_id",
										  "tax_country_code", "company_address_tax_id", "customer_email_as_per_tax_id",
										  "customers_nitku"],
										 as_dict=True)

		invoice_entry = {
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
																			  None] else customer_info.customer_id_number,
			"customer_name": customer_info.customer_name,
			"customer_address": "" if customer_info.company_address_tax_id in ["",
																			   None] else customer_info.company_address_tax_id,
			"customer_email_as_per_tax_id": "" if customer_info.customer_email_as_per_tax_id in ["",
																								 None] else customer_info.customer_email_as_per_tax_id,
			"customers_nitku": customer_info.customers_nitku,
			"items": []
		}

		si_items = frappe.db.get_all(
			"Sales Invoice Item",
			filters={
				"parent": invoice["name"],
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
											{"parent": invoice["name"], "idx": 1},
											["custom_use_temporary_rate", "rate", "custom_temporary_rate"],
											as_dict=True)

			invoice_entry["items"].append({
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

			tax_data["sales_invoices"].append(invoice_entry)

			frappe.db.set_value("Sales Invoice", invoice["name"], {
				"is_xml_generated": 1,
				"coretax_xml_exporter": doc.name
			})

	return tax_data


def generated_xml_file(tax_data, company_doc, doc):
	"""
	:param tax_data: List of Dictionary
	:param company_doc: Dictionary
	:param doc: Object
	"""

	template_dir = frappe.get_app_path('erpnext_indonesia_localization', "templates")
	env = Environment(loader = FileSystemLoader(template_dir))

	template = env.get_template('tax_invoice_bulk.jinja')
	output = template.render(customer_sales_invoice_docs=tax_data)

	file_name = f"Exporter {company_doc.company_name} {doc.start_invoice_date} to {doc.end_invoice_date}.xml"
	file_path = frappe.get_site_path('private', 'files', file_name)

	with open(file_path, "w", encoding="utf-8") as file:
		file.write(output)

	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_url": f"/private/files/{file_name}",
		"file_name": file_name,
		"attached_to_doctype": doc.doctype,
		"attached_to_name": doc.name,
	})

	file_doc.save(True)


def unlink_sales_invoices(doc_name):
	"""
	:param doc_name: String
	"""

	frappe.set_value("Sales Invoice", {"coretax_xml_exporter": doc_name}, {
		"is_xml_generated": 0,
		"coretax_xml_exporter": ""
	})

	frappe.delete_doc("File", frappe.get_value("File", {"attached_to_doctype": "Coretax XML Exporter", "attached_to_name": doc_name}, "name"))
