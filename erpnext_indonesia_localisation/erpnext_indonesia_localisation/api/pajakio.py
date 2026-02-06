import json
import requests
import frappe
import base64
import re

def create_vat_output(doc):
	frappe.utils.logger.set_log_level("DEBUG")
	logger = frappe.logger("pajak_io", with_more_info=True, allow_site=True, file_count=10)

	indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")
	key = bytes(indonesia_localisation_settings.get_password('pajakio_api_key'), 'utf-8')
	pajakio_api_key = base64.b64encode(key)

	url_create_vat = indonesia_localisation_settings.url_create_vat
	api_header = {
		"accept": "application/json",
		"content-type": "application/json",
		"Authorization": pajakio_api_key
	}

	# Populate barangjasa
	barangjasa = []
	for item in doc.barangjasa:
		barangjasa.append({
			"nama": re.sub('<[^<]+?>', '', item.nama),
			"jumlah": item.jumlah,
			"harga": item.harga,
			"dpp": item.dpp,
			"diskon": 0,
			"ppn": item.ppn,
			"tarifppnbm": item.tarifppnbm
		})

	# Populate Query
	query = {
		"autoUploadDjp": doc.autouploaddjp,
		"pengganti": doc.pengganti,
		"nofa": doc.nofa,
		"noInvoice": doc.noinvoice,
		"kdJenisTransaksi": doc.kdjenistransaksi,
		"idKeteranganTambahan": doc.idketerangantambahan,
		"barangJasa": barangjasa,
		"lawanTransaksi": {
			"npwp": doc.npwp,
			"nikPassport": doc.nikpassport,
			"nama": doc.customername,
			"alamatJalan": doc.alamatjalan,
			"kota": doc.kota,
			"telp": doc.telp
		},
		"tanggalFaktur": doc.tanggalfaktur,
		"masaPajak": doc.masapajak,
		"tahunPajak": doc.tahunpajak,
		"tarifPpn": doc.tarifppn,
		"terminPembayaran": doc.terminpembayaran,
		"terminDpp": doc.termindpp,
		"terminPpn": doc.terminppn,
		"terminPpnbm": doc.terminppnbm
	}
	response = requests.post(url_create_vat, headers=api_header, json=query)
	try:
		logger.info("----------------------------------")
		logger.debug(f"Request: {query}")
		logger.debug(f"Response: {response.json()}")
		logger.info("##################################")
		return response.json()
	except:
		return response.raise_for_status()


@frappe.whitelist()
def create_vat_output_js(name):
	doc = frappe.get_doc("VAT Output Metadata", name)
	indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")

	class AllowedTo:
		create_vat = indonesia_localisation_settings.create_vat_output
		check_detail = indonesia_localisation_settings.get_details_vat_output
		create_pdf = indonesia_localisation_settings.get_pdf_vat_output

	class RequestStatus:
		uploaded_but_not_processed = doc.transactionid and (doc.status == "To Be Reviewed" or doc.status == "Draft")
		approved_but_no_pdf = doc.status == "Approved" and not doc.vat_output_pdf_response
		pdf_has_been_generated = doc.status == "Received PDF" and doc.vat_output_pdf_response

	if RequestStatus.pdf_has_been_generated:
		message = "PDF has already been generated"
	elif RequestStatus.approved_but_no_pdf:
		message = proceed_to_get_pdf(doc, AllowedTo)
	elif RequestStatus.uploaded_but_not_processed:
		message = proceed_to_get_vat_output_details(doc, AllowedTo)
	elif AllowedTo.create_vat:
		message = create_vat(doc, AllowedTo)
	else:
		message = "Create VAT is turned off in Indonesia Localisation Settings"

	return message


def proceed_to_get_pdf(doc, allowed_to):
	if not allowed_to.create_pdf:
		return "Get VAT Output PDF is turned off in Indonesia Localisation Settings"

	response_msg = get_pdf_vat_output(doc)
	doc.vat_output_pdf_response = response_msg['message']
	try:
		request_code = str(response_msg['code'])
		pdf_successfully_generated = request_code == "200" and response_msg['message'] == 'SUCCESS GET PDF VAT OUTPUT'
	except:
		doc.status = "Draft"
		message = response_msg
		doc.save()
		return message

	if not pdf_successfully_generated:
		return "Failed to generate PDF"

	doc.status = "Received PDF"
	message = "PDF has been generated"
	doc.base64 = response_msg['data']['filePdf']
	doc.save()

	return message


def proceed_to_get_vat_output_details(doc, allowed_to):
	if not allowed_to.check_detail:
		return "Get VAT Output Details is turned off in Indonesia Localisation Settings"

	response_msg = get_vat_output_detail(doc)
	try:
		request_code = str(response_msg['code'])
	except:
		doc.status = "Draft"
		message = response_msg
		doc.save()
		return message

	if request_code != "200":
		doc.status = "Draft"
		message = response_msg['message']
		return message

	doc.status = "Approved"
	doc.nofa = response_msg['data'][0]['nofa']
	try:
		parent_invoice_doc = frappe.get_doc(doc.parent_doctype, doc.noinvoice)
	except DoesNotExistError:
		message = "Couldn't find the original invoice document for this doctype. Please try to recreate VAT Output Metadata for this document"
		return message

	doc.get_vat_pdf_response = str(response_msg['data'][0]["status"])
	parent_invoice_doc.nomor_faktur = doc.nofa
	parent_invoice_doc.save()
	doc.save()
	message = "VAT Output Approved"

	if allowed_to.create_pdf:
		create_vat_output_js(doc.name)

	return message


def create_vat(doc, allowed_to):
	response_msg = create_vat_output(doc)
	try:
		vat_has_been_requested = response_msg['code'] == 200 or response_msg['code'] == 201 or doc.transactionid
		draft_faktur_existed = response_msg['code'] == 400 and response_msg['message'] == 'Draft Faktur already exist'
	except:
		doc.create_vat_response = response_msg
		message = response_msg
		return message

	if vat_has_been_requested:
		doc.create_vat_response = response_msg['message']
		doc.transactionid = response_msg['data']['transactionId']
		message = "VAT Output Requested"
		doc.save()
		if allowed_to.check_detail:
			create_vat_output_js(doc.name)
	elif draft_faktur_existed:
		doc.status = 'Draft'
		doc.create_vat_response = response_msg[
									  'message'] + " .Please go to your Pajak.io account and retrieve Transaction ID for this invoice"
		message = response_msg['message']
		doc.save()
	else:
		doc.status = 'To Be Reviewed'
		doc.create_vat_response = "Error Code: " + str(response_msg['code']) + " | " + response_msg['message']
		message = response_msg['message']
		doc.save()

	return message


@frappe.whitelist()
def get_vat_output_detail(doc):
	indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")
	key = bytes(indonesia_localisation_settings.get_password('pajakio_api_key'), 'utf-8')
	pajakio_api_key = base64.b64encode(key)
	url_get_vat = indonesia_localisation_settings.url_get_vat + doc.transactionid

	api_header = {
		"accept": "application/json",
		"content-type": "application/json",
		"Authorization": pajakio_api_key
	}

	response = requests.get(url_get_vat, headers=api_header)

	try:
		return response.json()
	except:
		return response.raise_for_status()


def get_pdf_vat_output(doc):
	indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")
	key = bytes(indonesia_localisation_settings.get_password('pajakio_api_key'), 'utf-8')
	pajakio_api_key = base64.b64encode(key)
	url_get_vat = indonesia_localisation_settings.url_get_pdf_vat
	payload = [{"transactionId": doc.transactionid}]
	api_header = {
		"accept": "application/json",
		"content-type": "application/json",
		"Authorization": pajakio_api_key
	}

	response = requests.post(url_get_vat, json=payload, headers=api_header)

	try:
		return response.json()
	except:
		return response.raise_for_status()

@frappe.whitelist()
def upload_vat_output(doc):
	doc = frappe.get_doc("VAT Output Metadata", doc)

	indonesia_localisation_settings = frappe.get_single("Indonesia Localisation Settings")
	key = bytes(indonesia_localisation_settings.get_password('pajakio_api_key'), 'utf-8')
	pajakio_api_key = base64.b64encode(key)
	url_upload_vat = indonesia_localisation_settings.url_upload_vat
	payload = {"transactionId": doc.transactionid}
	api_header = {
		"accept": "application/json",
		"content-type": "application/json",
		"Authorization": pajakio_api_key
	}

	response = requests.post(url_upload_vat, json=payload, headers=api_header)

	try:
		res = response.json()
		if res["code"] == 200:
			doc.vat_upload_success = True
			doc.get_vat_pdf_response = str(res["message"])
			doc.save()
		return res
	except:
		return response.raise_for_status()
