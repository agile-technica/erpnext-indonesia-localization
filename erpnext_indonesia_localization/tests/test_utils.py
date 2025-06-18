from unittest.mock import MagicMock, patch
import sys

frappe_mock = MagicMock()
frappe_mock.whitelist = lambda : lambda x:x
sys.modules['frappe'] = frappe_mock
sys.modules['frappe.utils'] = frappe_mock

from erpnext_indonesia_localization.utils.template_tax import create_indonesia_localization_tax_template

def test_create_indonesia_localization_tax_template():
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

	result = create_indonesia_localization_tax_template(company_name)

	assert result == ["PPN Penjualan 12% - PTTC", "PPN Penjualan 11% - PTTC"]
	assert mock_db.get_value.call_args[0] == ("Company", company_name, "abbr")
	assert mock_db.exists.call_count == 2
	assert mock_get_doc.call_count == 2
	assert mock_doc_12.insert.call_count == 1
	assert mock_doc_11.insert.call_count == 1


@patch("erpnext_indonesia_localization.utils.template_tax.frappe")
def test_create_indonesia_localization_tax_template_when_templates_exist(mock_frappe):
	mock_db = frappe_mock.db
	mock_get_doc = MagicMock()
	frappe_mock.get_doc = mock_get_doc
	frappe_mock.utils.now.return_value = "2025-06-12 17:46:06.065257"

	company_name = "PT Test Company"
	abbr = "PTTC"

	mock_db.get_value.return_value = abbr

	mock_frappe.db.exists.side_effect = [True, True]

	result = create_indonesia_localization_tax_template(company_name)

	assert result is None
	assert mock_frappe.db.exists.call_count == 2
	assert mock_get_doc.call_count == 0
	assert mock_get_doc.return_value.insert.call_count == 0


@patch("erpnext_indonesia_localization.utils.template_tax.frappe")
def test_create_indonesia_localization_tax_template_when_one_of_template_missing(mock_frappe):
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

	result = create_indonesia_localization_tax_template(company_name)

	assert result == ["PPN Penjualan 12% - PTTC"]
	assert mock_db.get_value.call_args[0] == ("Company", company_name, "abbr")
	assert mock_db.exists.call_count == 2
	assert mock_get_doc.call_count == 1
	assert mock_doc_12.insert.call_count == 1