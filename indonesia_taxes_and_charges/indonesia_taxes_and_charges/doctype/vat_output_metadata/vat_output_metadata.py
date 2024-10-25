# Copyright (c) 2023, Agile Technica and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import base64

class VATOutputMetadata(Document):
	pass

@frappe.whitelist(allow_guest=True)
def convert_base64_to_pdf(docname):
	doc = frappe.get_doc("VAT Output Metadata", docname)
	base64_string = doc.base64
	try:
		base64_string = base64_string
		output_file = f"/tmp/pajak-io-{docname}.pdf"

		base64_to_pdf(base64_string, output_file)

		with open(output_file, 'rb') as file:
			frappe.local.response.filename = f"{docname}.pdf"
			frappe.local.response.filecontent = file.read()
			frappe.local.response.type = "download"

	except Exception as e:
		frappe.throw(_("Something went wrong while downloading the PDF."))

def base64_to_pdf(base64_string, output_file):
	pdf_data = base64.b64decode(base64_string)
	with open(output_file, 'wb') as file:
		file.write(pdf_data)


