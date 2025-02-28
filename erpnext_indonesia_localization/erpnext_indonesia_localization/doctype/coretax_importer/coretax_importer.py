# Copyright (c) 2025, Agile Technica and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document
from frappe.utils import getdate
from frappe.utils.xlsxutils import read_xlsx_file_from_attached_file


class CoreTaxImporter(Document):
	@frappe.whitelist()
	def generate_preview(self, file):
		data = read_xlsx_file_from_attached_file(file_url=file)
		table_content = ""

		for idx, row in enumerate(data):
			row_content = ""
			for content in row:
				row_content += f"""
					\n<td>{content}</td>
				"""
			table_content += f"""
				<tr>
					{row_content}
				</tr>
			"""

			if idx == 9:
				break

		data_preview = """
			<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
			</head>
			
			<body>
				<h3>Preview</h3>
				<table class="table table-bordered text-nowrap table-responsive">
					%s
				</table>
				
				<h5>Showing 10 row of total %d rows.</h5>
			</body>
			</html>
		""" % (table_content, len(data))

		return data_preview

	@frappe.whitelist()
	def start_import(self, file):
		frappe.enqueue(
			method=update_sales_invoice_from_xlsx,
			queue="long",
			file=file,
			doc_name=self.name
		)


def update_sales_invoice_from_xlsx(file, doc_name):
	datas = read_xlsx_file_from_attached_file(file_url=file)
	error = []

	for idx, row in enumerate(datas[1:]):
		try:
			frappe.db.set_value(
				"Sales Invoice",
				row[datas[0].index("Referensi")],
				{
					"tanggal_faktur_pajak": getdate(row[datas[0].index("Tanggal Faktur Pajak")]),
					"nomor_faktur_pajak": row[datas[0].index("Nomor Faktur Pajak")],
					"coretax_status": row[datas[0].index("Status Faktur")]
				}
			)
		except Exception as e:
			error.append({
				"row": idx + 2,
				"referensi": row[datas[0].index("Referensi")],
				"error_message": str(e)
			})

	if error:
		frappe.log_error(
			title="Failed to Import Faktur Pajak",
			message=str(error)
		)

	status = "Succeed" if not error else "Update Failed"
	frappe.db.set_value("CoreTax Importer", doc_name, "importer_status", status)