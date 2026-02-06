from unittest.mock import MagicMock, patch
import sys
import pytest

frappe_mock = MagicMock()
frappe_mock.whitelist = lambda : lambda x:x
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = frappe_mock

from erpnext_indonesia_localisation.utils.template_tax import create_indonesia_localisation_tax_template, create_tax_template

def test_create_indonesia_localisation_tax_template():
	mock_db = frappe_mock.db
	mock_get_doc = MagicMock()
	frappe_mock.get_doc = mock_get_doc
	frappe_mock.utils.now.return_value = "2025-06-12 17:46:06.065257"

	company_name = "PT Test Company"
	abbr = "PTTC"

	mock_db.get_value.return_value = abbr

	mock_db.exists.side_effect = [False, False]

	mock_doc_12 = MagicMock()
	mock_doc_12.name = "PPN Penjualan 12% - PTTC"

	mock_doc_11 = MagicMock()
	mock_doc_11.name = "PPN Penjualan 11% - PTTC"

	mock_get_doc.side_effect = [mock_doc_12, mock_doc_11]
	mock_doc_12.insert.return_value = None
	mock_doc_11.insert.return_value = None

	result = create_indonesia_localisation_tax_template(company_name)

	assert result == ["PPN Penjualan 12% - PTTC", "PPN Penjualan 11% - PTTC"]
	assert mock_db.get_value.call_args[0] == ("Company", company_name, "abbr")
	assert mock_db.exists.call_count == 2
	assert mock_get_doc.call_count == 2
	assert mock_doc_12.insert.call_count == 1
	assert mock_doc_11.insert.call_count == 1


@patch("erpnext_indonesia_localisation.utils.template_tax.frappe")
def test_create_indonesia_localisation_tax_template_when_templates_exist(mock_frappe):
	mock_db = frappe_mock.db
	mock_get_doc = MagicMock()
	frappe_mock.get_doc = mock_get_doc
	frappe_mock.utils.now.return_value = "2025-06-12 17:46:06.065257"

	company_name = "PT Test Company"
	abbr = "PTTC"

	mock_db.get_value.return_value = abbr

	mock_frappe.db.exists.side_effect = [True, True]

	result = create_indonesia_localisation_tax_template(company_name)

	assert result is None
	assert mock_frappe.db.exists.call_count == 2
	assert mock_get_doc.call_count == 0
	assert mock_get_doc.return_value.insert.call_count == 0


@patch("erpnext_indonesia_localisation.utils.template_tax.frappe")
def test_create_indonesia_localisation_tax_template_when_one_of_template_missing(mock_frappe):
	mock_db = mock_frappe.db
	mock_get_doc = MagicMock()
	mock_frappe.get_doc = mock_get_doc
	frappe_mock.utils.now.return_value = "2025-06-12 17:46:06.065257"

	company_name = "PT Test Company"
	abbr = "PTTC"

	mock_db.get_value.return_value = abbr

	mock_db.exists.side_effect = [False, True]

	mock_doc_12 = MagicMock()
	mock_doc_12.name = "PPN Penjualan 12% - PTTC"

	mock_get_doc.side_effect = [mock_doc_12]
	mock_doc_12.insert.return_value = None

	result = create_indonesia_localisation_tax_template(company_name)

	assert result == ["PPN Penjualan 12% - PTTC"]
	assert mock_db.get_value.call_args[0] == ("Company", company_name, "abbr")
	assert mock_db.exists.call_count == 2
	assert mock_get_doc.call_count == 1
	assert mock_doc_12.insert.call_count == 1


@patch("erpnext_indonesia_localisation.utils.template_tax.now")
@patch("erpnext_indonesia_localisation.utils.template_tax.frappe")
def test_create_tax_template_when_success(mock_frappe, mock_now):
	mock_get_doc = MagicMock()
	mock_frappe.get_doc = mock_get_doc
	mock_now.return_value = "2025-06-12 17:46:06.065257"

	company = "PT Test Company"
	abbr = "PTTC"
	rate = 12

	mock_tax_template = MagicMock()
	mock_tax_template.name = f"PPN Penjualan {rate}% - {abbr}"
	mock_tax_template.insert.return_value = None

	mock_get_doc.return_value = mock_tax_template


	result = create_tax_template(company, abbr, rate)

	mock_get_doc.assert_called_with({
		"doctype": "Sales Taxes and Charges Template",
		"company": "PT Test Company",
		"title": "PPN Penjualan 12%",
		"disabled": 0,
		"is_default": 0,
		"name": "PPN Penjualan 12% - PTTC",
		"tax_category": None,
		"creation": "2025-06-12 17:46:06.065257",
		"modified": "2025-06-12 17:46:06.065257",
		"taxes": [
			{
				"account_currency": "IDR",
				"account_head": f"VAT - PTTC",
				"base_tax_amount": 0.0,
				"base_tax_amount_after_discount_amount": 0.0,
				"base_total": 0.0,
				"charge_type": "On Net Total",
				"cost_center": f"Main - PTTC",
				"description": "Hutang Pajak",
				"dont_recompute_tax": 0,
				"included_in_paid_amount": 0,
				"included_in_print_rate": 0,
				"item_wise_tax_detail": None,
				"parent": "PPN Penjualan 12% - PTTC",
				"parentfield": "taxes",
				"parenttype": "Sales Taxes and Charges Template",
				"use_temporary_rate": True,
				"rate": 11,
				"temporary_rate": 12,
				"row_id": None,
				"tax_amount": 0.0,
				"tax_amount_after_discount_amount": 0.0,
				"total": 0.0
			}
		]
	})

	assert result == f"PPN Penjualan {rate}% - {abbr}"
	assert mock_get_doc.call_count == 1
	assert mock_tax_template.insert.call_count == 1



@patch("erpnext_indonesia_localisation.utils.template_tax.frappe")
def test_create_tax_template_when_parameter_missing(mock_frappe):
	mock_get_doc = MagicMock()
	mock_frappe.get_doc = mock_get_doc

	company = "PT Test Company"
	abbr = "PTTC"
	rate = ""

	mock_frappe.throw.side_effect = Exception("Please provide company, abbreviation, and rate.")

	with pytest.raises(Exception, match="Please provide company, abbreviation, and rate."):
		create_tax_template(company, abbr, rate)

	assert mock_get_doc.call_count == 0
