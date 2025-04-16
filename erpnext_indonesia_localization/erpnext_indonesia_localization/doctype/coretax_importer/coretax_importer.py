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
		total_rows = len(data) - 1

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

			if idx == 10:
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
					{content}
				</table>

				<h5>Showing {displayed_rows} out of {row_count} row(s).</h5>
			</body>
			</html>
		""".format(
			content=table_content,
			row_count=total_rows,
			displayed_rows=min(10, total_rows)
			)

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
	import_logs = []

	for idx, row in enumerate(datas[1:]):
		try:
			referensi = row[datas[0].index("Referensi")]
			tanggal_faktur_pajak = row[datas[0].index("Tanggal Faktur Pajak")]
			nomor_faktur_pajak = row[datas[0].index("Nomor Faktur Pajak")]
			status_faktur = row[datas[0].index("Status Faktur")]

			is_invoice_exsist = frappe.db.exists(
				"Sales Invoice",
				{"name": referensi}
			)

			if is_invoice_exsist:
				check_empty_value({
					"Tanggal Faktur Pajak": tanggal_faktur_pajak,
					"Status Faktur": status_faktur
				})

				validation_coretax_status(status_faktur, nomor_faktur_pajak)

				frappe.db.set_value(
					"Sales Invoice",
					row[datas[0].index("Referensi")],
					{
						"tanggal_faktur_pajak": getdate(tanggal_faktur_pajak),
						"nomor_faktur_pajak": nomor_faktur_pajak,
						"coretax_status": status_faktur
					}
				)
			else:
				raise frappe.exceptions.DoesNotExistError("Invoice with reference number not found.")

		except Exception as e:
			import_logs.append({
				"row": idx + 2,
				"status": "Failure",
				"message": str(e)
			})

	if import_logs:
		frappe.db.rollback()
		import_logs_preview = "".join(
			f"""<tr><td>{log['row']}</td><td><div class="indicator red">{log['status']}</div></td><td>{log['message']}</td></tr>"""
			for log in import_logs
		)

		html = """
		<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
			</head>

			<body>
				<h3>Import Error Log</h3>
				<table class="table table-bordered text-nowrap">
					<tr>
						<th>Row</th>
						<th>Status</th>
						<th>Message</th>
					</tr>
					%s
				</table>
			</body>
		</html>
		""" % import_logs_preview

		frappe.set_value("CoreTax Importer", doc_name, {
			"importer_status": "Failed",
			"html": html
		})
	else:
		frappe.set_value("CoreTax Importer", doc_name, {
			"importer_status": "Succeed",
			"html": ""
		})


def check_empty_value(values):
	empty_fields = [field for field, value in values.items() if not value]

	if empty_fields:
		raise frappe.exceptions.ValidationError(
			f"{', '.join(empty_fields)} is empty."
		)


def validation_coretax_status(coretax_status, nomor_faktur_pajak):
	if coretax_status not in ["APPROVED", "AMENDED", "REJECTED"]:
		raise frappe.exceptions.ValidationError(
			f"Status Faktur {coretax_status} is not valid. It should be APPROVED, AMENDED, or REJECTED."
		)
	elif coretax_status == "APPROVED":
		if not nomor_faktur_pajak:
			raise frappe.exceptions.ValidationError(
				"Nomor Faktur Pajak is required when Status Faktur is APPROVED."
			)
