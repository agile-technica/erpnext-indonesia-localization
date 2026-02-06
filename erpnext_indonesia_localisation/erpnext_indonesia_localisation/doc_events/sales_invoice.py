import frappe
from frappe.utils import cint
from ..api.pajakio import create_vat_output
from ...utils.data import get_tax_prefix_code


# Procedures to generate VOM doctype
@frappe.whitelist()
def procedure_to_create_vom(name, doctype):
	doc = frappe.get_doc(doctype, name)
	indonesia_localisation_settings = frappe.get_single('Indonesia Localisation Settings')
	NOFA_SOURCE = indonesia_localisation_settings.tax_invoice_number_source.upper()
	PAJAKIO_NOFA = 'PAJAK.IO'
	INHOUSE_NOFA = 'TAX INVOICE NUMBER DOCTYPE'

	title = 'Error Registering Tax Invoice Number'
	message = "Please check Indonesia Localisation Settings configurations"

	if NOFA_SOURCE == PAJAKIO_NOFA:
		success_status, message = create_vat_output_metadata(doc, indonesia_localisation_settings)
		if success_status:
			title = 'VAT Output Metadata Created'
		else:
			title = 'Error Registering Tax Invoice Number'
	elif NOFA_SOURCE == INHOUSE_NOFA:
		success_status, message = link_tax_invoice_number(doc)
		if success_status:
			title = 'Succesfully Registered Tax Invoice Number'
			create_vat_output_metadata(doc, indonesia_localisation_settings)
	return message, title


@frappe.whitelist()
def create_vom_via_button(name, doctype):
	message, title = procedure_to_create_vom(name, doctype)
	frappe.msgprint(
		msg=message,
		title=title
	)

	return


@frappe.whitelist()
def create_vom_via_cronjob(name, doctype):
	procedure_to_create_vom(name, doctype)

	return


@frappe.whitelist()
def link_tax_invoice_number(doc):
	if doc.nomor_faktur:
		incorrectly_linked = frappe.db.get_value('Tax Invoice Number', doc.nomor_faktur, 'sales_invoice') != doc.name
		if incorrectly_linked:
			message = 'Tax Invoice Number already linked to another SI'
			return False, message
		return True

	available_nofa = frappe.db.get_list('Tax Invoice Number', filters={'status': 'Available'}, pluck='name')
	if not available_nofa:
		message = 'No Tax Invoice Number available'
		return False, message

	nofa = available_nofa[0]

	frappe.db.set_value('Tax Invoice Number', nofa, 'sales_invoice', doc.name)
	frappe.db.set_value('Tax Invoice Number', nofa, 'status', 'Used')
	frappe.db.set_value('Tax Invoice Number', nofa, 'linked_datetime', frappe.utils.now())

	message = 'Successfully linked invoice to tax invoice number'

	return True, message


def check_mandatory_fields(metadata_doc):
	empty_mandatory_fields = []
	mandatory_fields = ['kdjenistransaksi', "nama", "alamatjalan", "tarifppn", "terminpembayaran"]
	mandatory_item_fields = ['nama', 'harga', 'jumlah', 'dpp', 'ppn']

	for field in mandatory_fields:
		if not metadata_doc.get(field):
			empty_mandatory_fields.append(field)

	for item in metadata_doc.barangjasa:
		for field in mandatory_item_fields:
			if not item.get(field):
				empty_mandatory_fields.append(field + ' item')

	safe_to_proceed = True

	if len(empty_mandatory_fields) > 0:
		safe_to_proceed = False

	return safe_to_proceed, empty_mandatory_fields


@frappe.whitelist()
def create_vat_output_metadata(doc, indonesia_localisation_settings):
	metadata_doc = frappe.new_doc('VAT Output Metadata')

	NOFA_SOURCE = indonesia_localisation_settings.tax_invoice_number_source.upper()
	INHOUSE_NOFA = 'TAX INVOICE NUMBER DOCTYPE'
	METADATA_DRAFT_STATUS = 'To Be Reviewed'
	customer_details = frappe.get_doc("Customer", doc.customer)

	if not customer_details.customer_primary_address:
		message = "Please complete primary address for " + str(customer_details.customer_name)
		return False, message
	customer_address = frappe.get_doc("Address", customer_details.customer_primary_address)

	if not customer_details.mobile_no:
		message = "Please complete primary contact number for " + str(customer_details.customer_name)
		return False, message

	if doc.nomor_faktur and NOFA_SOURCE == INHOUSE_NOFA:
		metadata_doc.nofa = doc.nomor_faktur

	metadata_doc.autouploaddjp = indonesia_localisation_settings.autouploaddjp
	metadata_doc.noinvoice = doc.name

	if doc.kdjenistransaksi:
		metadata_doc.kdjenistransaksi = doc.kdjenistransaksi.strip()
	else:
		kode_pajak = doc.kode_pajak.split("-")
		metadata_doc.kdjenistransaksi = kode_pajak[0].strip()

	if not doc.idketerangantambahan:
		metadata_doc.idketerangantambahan = doc.idketerangantambahan
	else:
		metadata_doc.idketerangantambahan = doc.idketerangantambahan.strip()

	metadata_doc.tanggalfaktur = frappe.utils.formatdate(frappe.utils.today(), "YYYY-mm-dd")
	metadata_doc.masapajak = frappe.utils.formatdate(frappe.utils.today(), "mm").strip()
	metadata_doc.tahunpajak = frappe.utils.formatdate(frappe.utils.today(), "yyyy").strip()
	metadata_doc.parent_doctype = doc.doctype

	tariff = 0
	for account_head in doc.taxes:
		tariff += cint(account_head.rate)

	metadata_doc.tarifppn = tariff
	metadata_doc.termindpp = doc.termin_dpp
	metadata_doc.terminppn = doc.termin_ppn
	metadata_doc.terminppnbm = doc.termin_ppnbm

	if doc.terminpembayaran:
		metadata_doc.terminpembayaran = doc.terminpembayaran.strip()
	else:
		termin = doc.invoice_payment_type.split("-")
		metadata_doc.terminpembayaran = termin[0].strip()

	for item in doc.items:
		metadata_doc.append('barangjasa', {
			"nama": item.description,
			"jumlah": item.qty,
			"harga": item.rate,
			"dpp": item.qty * item.rate,
			"ppn": (item.amount * (tariff / 100)),
			"tarifppnbm": 0
		})

	metadata_doc.npwp = doc.tax_id.replace('.', '')
	metadata_doc.nikpassport = None
	metadata_doc.nama = doc.customer
	metadata_doc.alamatjalan = customer_details.company_address_tax_id
	metadata_doc.kota = customer_address.city
	metadata_doc.telp = customer_details.mobile_no
	metadata_doc.status = METADATA_DRAFT_STATUS

	safe_to_proceed, empty_mandatory_fields = check_mandatory_fields(metadata_doc)

	if not safe_to_proceed:
		message = 'Required Pajak.io API field(s) that are still empty: ' + ', '.join(empty_mandatory_fields)
		return False, message

	metadata_doc.save()

	if indonesia_localisation_settings.auto_call_pajakios_api:
		create_vat_output(metadata_doc)
	message = "Successfully Registered Tax Invoice Number"

	return True, message


def set_tin_status_before_cancel_si(si_doc, method=None):
	if si_doc.tax_invoice_number:
		if frappe.get_value("Customer", si_doc.customer, "customer_pkp"):
			tin_name = frappe.get_value("Tax Invoice Number", {"linked_si": si_doc.name}, "name")

			tin_doc = frappe.get_doc("Tax Invoice Number", tin_name)
			tin_doc.rollback_tin_to_available(si_doc)

			tin_exporter_item = frappe.db.exists("Tax Invoice Exporter Item", {
				"sales_invoice": si_doc.name
			})
			frappe.db.set_value(
				"Tax Invoice Exporter Item",
				tin_exporter_item,
				'is_invoice_cancelled',
				True,
				update_modified=False
			)
		else:
			tin_name = frappe.get_value("List of Sales Invoice", {"sales_invoice_id": si_doc.name}, "parent")
			tin_doc = frappe.get_doc("Tax Invoice Number", tin_name)

			tin_exporter_item = frappe.db.exists("Tax Invoice Exporter Item", {
				"sales_invoice": si_doc.name
			})

			frappe.db.set_value(
				"Tax Invoice Exporter Item",
				tin_exporter_item,
				'is_invoice_cancelled',
				True,
				update_modified=False
			)

			for invoice in tin_doc.list_of_sales_invoice:
				if invoice.sales_invoice_id == si_doc.name:
					invoice.is_invoice_cancelled = 1

			if check_if_all_invoice_cancelled(tin=tin_doc):
				tin_doc.rollback_tin_to_available(si_doc)
			else:
				tin_doc.tax_invoice_number = "011" + tin_doc.tax_invoice_number[3:]
				tin_doc.save()

		frappe.msgprint(
			msg=f'Tax Invoice Number {si_doc.tax_invoice_number} has been unlinked',
			title='Notification',
			indicator= 'green'
		)


def set_si_had_tin_before(si_doc, _):
	if si_doc.tax_invoice_number:
		si_doc.db_set("custom_si_had_tin_before", 1)


def check_if_all_invoice_cancelled(tin):
	for invoice in tin.list_of_sales_invoice:
		if invoice.is_invoice_cancelled == 0:
			return False

	return True


def calculate_other_tax_base_amount_and_total(doc, method):
	if doc.taxes_and_charges:
		tax_template_doc = frappe.get_value("Sales Taxes and Charges",
											{"parent": doc.taxes_and_charges, "idx": 1},
											["use_temporary_rate", "rate", "temporary_rate"],
											as_dict=True)
		doc.total_other_tax_base = 0
		doc.total_luxury_goods_tax = 0

		if tax_template_doc.use_temporary_rate:
			for item in doc.items:
				item.other_tax_base_amount = item.net_amount * tax_template_doc.rate / tax_template_doc.temporary_rate
				item.vat_amount = item.other_tax_base_amount * tax_template_doc.temporary_rate / 100
				doc.total_other_tax_base += item.other_tax_base_amount
				doc.total_luxury_goods_tax += item.luxury_goods_tax_amount
		else:
			for item in doc.items:
				item.vat_amount = item.net_amount * tax_template_doc.rate / 100
				doc.total_other_tax_base += item.net_amount
				doc.total_luxury_goods_tax += item.luxury_goods_tax_amount


def set_sales_taxes_template_values(doc, method):
	fields_to_sync = ['transaction_code', 'tax_additional_info', 'tax_facility_stamp']

	if doc.taxes_and_charges:
		taxes_template = frappe.db.get_value(
			"Sales Taxes and Charges Template",
			doc.taxes_and_charges,
			['transaction_code', 'tax_additional_info', 'tax_facility_stamp'],
			as_dict=True
		)
	else:
		taxes_template = frappe.db.get_value(
			"Sales Taxes and Charges Template",
			{
				"company": doc.company,
				"is_default": True
			},
			fields_to_sync,
			as_dict=True
		)

	if taxes_template:
		for field in fields_to_sync:
			if not doc.get(field):
				doc.set(field, taxes_template.get(field))
