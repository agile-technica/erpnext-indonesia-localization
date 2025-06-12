from unittest.mock import MagicMock
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

	mock_doc = MagicMock()
	mock_get_doc.return_value = mock_doc
	mock_doc.insert.return_value = None

	result = create_indonesia_localization_tax_template(company_name)

	assert result is True
	assert mock_db.get_value.call_args[0] == ("Company", company_name, "abbr")
	assert mock_db.exists.call_count == 2
	assert mock_get_doc.call_count == 2
	assert mock_doc.insert.call_count == 2
