import pytest
from unittest.mock import patch, MagicMock, ANY

from erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer import CoreTaxImporter, update_sales_invoice_from_xlsx, check_empty_value


mock_preview_data = [
	["Referensi", "Tanggal Faktur Pajak", "Nomor Faktur Pajak", "Status Faktur"],
	["SI-2025-001", "2025-03-01", "111111", "Success"],
	["SI-2025-002", "2025-03-01", "222222", "Success"],
	["SI-2025-003", "2025-03-01", "333333", "Success"]
]

mock_preview_data_more_than_ten = [["Header1", "Header2"]] + [["Row" + str(i), "Data" + str(i)] for i in range(1, 15)]


@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_generate_preview_with_less_than_equal_ten_row(mock_read_xlsx):
	"""Test the generate_preview method with a small dataset (less than 10 rows)"""
	# Arrange
	mock_read_xlsx.return_value = mock_preview_data
	file_url = "path/to/test_file.xlsx"
	doc = MagicMock()

	# Act
	result = CoreTaxImporter.generate_preview.__wrapped__(doc, file=file_url)

	# Assert
	mock_read_xlsx.assert_called_once_with(file_url=file_url)
	for row in mock_preview_data:
		for cell in row:
			assert str(cell) in result
	assert "Showing 3 out of 3 row(s)" in result

@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_generate_preview_with_more_than_ten_row(mock_read_xlsx):
	"""Test the generate_preview method with a dataset larger than 10 rows"""
	# Arrange
	mock_read_xlsx.return_value = mock_preview_data_more_than_ten
	file_url = "path/to/large_file.xlsx"
	doc = MagicMock()

	# Act
	result = CoreTaxImporter.generate_preview.__wrapped__(doc, file=file_url)

	# Assert
	mock_read_xlsx.assert_called_once_with(file_url=file_url)
	assert "Row11" not in result
	assert "Row10" in result
	assert "Showing 10 out of 14 row(s)" in result


@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_generate_preview_with_empty_data(mock_read_xlsx):
	"""Test the generate_preview method with empty data"""

	# Arrange
	mock_read_xlsx.return_value = [["Header1", "Header2"]]
	file_url = "path/to/empty_file.xlsx"
	doc = MagicMock()

	# Act
	result = CoreTaxImporter.generate_preview.__wrapped__(doc, file=file_url)

	# Assert
	mock_read_xlsx.assert_called_once_with(file_url=file_url)
	assert "Showing 0 out of 0 row(s)" in result

@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file",
	side_effect=Exception("File error"))
def test_generate_preview_with_file_error(mock_read_xlsx):
	"""Test handling of file errors"""

	# Arrange
	file_url = "path/to/nonexistent_file.xlsx"
	doc = MagicMock()

	# Act
	with pytest.raises(Exception) as excinfo:
		CoreTaxImporter.generate_preview.__wrapped__(doc, file=file_url)

	# Assert
	assert "File error" in str(excinfo.value)
	mock_read_xlsx.assert_called_once_with(file_url=file_url)


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.getdate")
@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.frappe")
@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_update_sales_invoice_success(mock_read_xlsx, mock_frappe, mock_getdate):
	mock_read_xlsx.return_value = mock_preview_data
	mock_frappe.db.exists.return_value = True
	mock_getdate.side_effect = lambda x: x

	update_sales_invoice_from_xlsx(file="path/to/test_file.xlsx", doc_name="IMPORT-001")

	assert mock_frappe.db.set_value.call_count == len(mock_preview_data) - 1

	mock_frappe.set_value.assert_called_once_with("CoreTax Importer", "IMPORT-001", {
		"importer_status": "Update Succeed",
		"html": ""
	})


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.frappe")
@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_update_sales_invoice_failed(mock_read_xlsx, mock_frappe):
	mock_read_xlsx.return_value = mock_preview_data
	mock_frappe.db.exists.return_value = False
	mock_frappe.exceptions.DoesNotExistError = Exception

	update_sales_invoice_from_xlsx(file="path/to/test_file.xlsx", doc_name="IMPORT-001")

	mock_frappe.db.rollback.assert_called_once()
	mock_frappe.set_value.assert_called_once_with("CoreTax Importer", "IMPORT-001",{
		"importer_status": "Update Failed",
		"html":  ANY
	})


@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.getdate")
@patch("erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.frappe")
@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
def test_update_sales_invoice_validation_error(mock_read_xlsx, mock_frappe, mock_getdate):
	mock_read_xlsx.return_value = mock_preview_data
	mock_frappe.exceptions.DoesNotExistError = Exception
	mock_getdate.side_effect = lambda x: x
	count_set_value = 0

	def mock_exists(doctype, filters):
		nonlocal count_set_value

		if isinstance(filters, dict):
			ref_name = filters.get("name")
			existing_refs = [row[0] for row in mock_preview_data[1:]]

			if ref_name in existing_refs and ref_name != "SI-2025-002":
				count_set_value += 1

				return ref_name

			return None

		return True

	mock_frappe.db.exists.side_effect = mock_exists

	update_sales_invoice_from_xlsx(file="path/to/test_file.xlsx", doc_name="IMPORT-001")

	assert mock_frappe.db.set_value.call_count == count_set_value

	mock_frappe.db.rollback.assert_called_once()
	mock_frappe.set_value.assert_called_once_with("CoreTax Importer", "IMPORT-001", {
		"importer_status": "Update Failed",
		"html": ANY
	})


def test_should_be_failed_if_several_fields_empty():
	valid_data = {
		"Tanggal Faktur Pajak": "2025-03-01",
		"Nomor Faktur Pajak": "111111",
		"Status Faktur": "Success"
	}
	invalid_data_1 = {
		"Tanggal Faktur Pajak": "",
		"Nomor Faktur Pajak": "111111",
		"Status Faktur": "Success"
	}
	invalid_data_2 = {
		"Tanggal Faktur Pajak": "2025-03-01",
		"Nomor Faktur Pajak": "",
		"Status Faktur": "Success"
	}
	invalid_data_3 = {
		"Tanggal Faktur Pajak": "",
		"Nomor Faktur Pajak": "",
		"Status Faktur": ""
	}

	check_empty_value(valid_data)

	with pytest.raises(Exception,
					   match="Tanggal Faktur Pajak is empty"):
		check_empty_value(invalid_data_1)

	with pytest.raises(Exception,
					   match="Nomor Faktur Pajak is empty"):
		check_empty_value(invalid_data_2)

	with pytest.raises(Exception,
					   match="Tanggal Faktur Pajak, Nomor Faktur Pajak, Status Faktur is empty"):
		check_empty_value(invalid_data_3)
