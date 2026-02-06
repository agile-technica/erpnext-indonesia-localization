from unittest.mock import patch, MagicMock, call
from erpnext_indonesia_localisation.utils import install


@patch("erpnext_indonesia_localisation.utils.install.frappe")
@patch("erpnext_indonesia_localisation.utils.install.shutil.copy")
@patch("erpnext_indonesia_localisation.utils.install.os.path.exists")
@patch("erpnext_indonesia_localisation.utils.install.create_file_doc")
@patch("erpnext_indonesia_localisation.utils.install.create_run_doc_data_import")
def test_import_coretax_master_data(mock_run_import, mock_create_file, mock_exists, mock_copy, mock_frappe):
	mock_exists.return_value = True
	mock_create_file.side_effect = lambda filename: f"/files/{filename}"

	install.import_coretax_master_data()

	assert mock_copy.call_count == 5
	assert mock_create_file.call_count == 5
	assert mock_run_import.call_count == 5


@patch("erpnext_indonesia_localisation.utils.install.frappe")
@patch("erpnext_indonesia_localisation.utils.install.shutil.copy")
@patch("erpnext_indonesia_localisation.utils.install.os.path.exists")
@patch("erpnext_indonesia_localisation.utils.install.create_file_doc")
@patch("erpnext_indonesia_localisation.utils.install.create_run_doc_data_import")
def test_missing_one_file(mock_run_import, mock_create_file, mock_exists, mock_copy, mock_frappe):
	def exists_side_effect(path):
		return "Barang Jasa" not in path

	mock_exists.side_effect = exists_side_effect
	mock_create_file.side_effect = lambda filename: f"/files/{filename}"
	install.import_coretax_master_data()

	assert mock_copy.call_count == 4
	assert mock_create_file.call_count == 4
	assert mock_run_import.call_count == 4

	skipped = "CoreTax Barang Jasa Ref.xlsx"
	filenames_used = [call.args[0] for call in mock_create_file.call_args_list]

	assert skipped not in filenames_used


@patch("erpnext_indonesia_localisation.utils.install.frappe")
def test_create_get_doc(mock_frappe):
	mock_file_doc = MagicMock()
	mock_file_doc.file_url = "files/testfile.xlsx"
	mock_frappe.get_doc.return_value = mock_file_doc

	result = install.create_file_doc("testfile.xlsx")

	mock_frappe.get_doc.assert_called_once_with({
		"doctype": "File",
		"file_url": "/files/testfile.xlsx",
		"file_name": "testfile.xlsx"
	})

	mock_file_doc.insert.assert_called_once()
	assert result == "files/testfile.xlsx"


@patch("erpnext_indonesia_localisation.utils.install.start_import")
@patch("erpnext_indonesia_localisation.utils.install.frappe")
def test_create_run_doc_data_import(mock_frappe, mock_start_import):
	mock_data_import = MagicMock()
	mock_data_import.name = "DATA-IMPORT-001"
	mock_frappe.get_doc.return_value = mock_data_import

	doctype = "CoreTax Additional Info Ref"
	file_url = "/files/testfile.xlsx"

	install.create_run_doc_data_import(doctype, file_url)

	mock_frappe.get_doc.assert_called_once_with({
		"doctype": "Data Import",
		"reference_doctype": doctype,
		"import_type": "Insert New Records",
		"submit_after_import": 0,
		"import_file": file_url
	})

	mock_data_import.insert.assert_called_once_with(ignore_permissions=True)
	mock_start_import.assert_called_once_with("DATA-IMPORT-001")
