from unittest.mock import patch, MagicMock, call
from erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice import set_sales_taxes_template_values


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice.frappe")
def test_set_values_from_specific_taxes_and_charges(mock_frappe):
	mock_doc = MagicMock()
	mock_doc.taxes_and_charges = "PPN Penjualan 12%"
	mock_doc.get.return_value = None

	mock_frappe.db.get_value.return_value = {
		"transaction_code": "03",
		"tax_additional_info": "TD.00501",
		"tax_facility_stamp": "TD.01101"
	}

	set_sales_taxes_template_values(mock_doc, "after_insert")

	mock_frappe.db.get_value.assert_called_once_with(
		"Sales Taxes and Charges",
		"PPN Penjualan 12%",
		["transaction_code", "tax_additional_info", "tax_facility_stamp"],
		as_dict=True
	)

	mock_doc.set.assert_has_calls([
		call('transaction_code', '03'),
		call('tax_additional_info', 'TD.00501'),
		call('tax_facility_stamp', 'TD.01101')
	])

	assert mock_doc.set.call_count == 3


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice.frappe")
def test_set_values_from_default_template(mock_frappe):
	mock_doc = MagicMock()
	mock_doc.taxes_and_charges = None
	mock_doc.get.return_value = None
	mock_doc.company = "PT Test Company"

	mock_frappe.db.get_value.return_value = {
		"transaction_code": "01",
		"tax_additional_info": "TD.00501",
		"tax_facility_stamp": "TD.01101"
	}

	set_sales_taxes_template_values(mock_doc, "after_insert")

	mock_frappe.db.get_value.assert_called_once_with(
		'Sales Taxes and Charges Template',
		{
			'company': 'PT Test Company',
			'is_default': True
		},
		['transaction_code', 'tax_additional_info', 'tax_facility_stamp'],
		as_dict=True
	)

	mock_doc.set.assert_has_calls([
		call('transaction_code', '01'),
		call('tax_additional_info', 'TD.00501'),
		call('tax_facility_stamp', 'TD.01101')
	])

	assert mock_doc.set.call_count == 3


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice.frappe")
def test_do_not_overwrite_existing_values(mock_frappe):
	mock_doc = MagicMock()
	mock_doc.taxes_and_charges = "PPN Penjualan 12%"

	mock_doc.get.side_effect = [
		"01",
		"TD.00501",
		None
	]

	mock_frappe.db.get_value.return_value = {
		"transaction_code": "01",
		"tax_additional_info": "TD.00501",
		"tax_facility_stamp": "TD.01101"
	}

	set_sales_taxes_template_values(mock_doc, "after_insert")

	mock_doc.set.assert_has_calls([
        call('tax_facility_stamp', 'TD.01101')
    ])

	assert mock_doc.set.call_count == 1
