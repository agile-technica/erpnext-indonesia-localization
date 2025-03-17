import pytest
from unittest.mock import patch, MagicMock
from erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_importer.coretax_importer import CoreTaxImporter


mock_preview_data = [
	["Header1", "Header2", "Header3"],
	["Row1 Col1", "Row1 Col2", "Row1 Col3"],
	["Row2 Col1", "Row2 Col2", "Row2 Col3"],
	["Row3 Col1", "Row3 Col2", "Row3 Col3"],
]

mock_preview_data_more_than_ten = [["Header1", "Header2"]] + [["Row" + str(i), "Data" + str(i)] for i in range(1, 15)]


@patch(
	"erpnext_indonesia_localization.erpnext_indonesia_localization.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
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
	"erpnext_indonesia_localization.erpnext_indonesia_localization.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
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
	"erpnext_indonesia_localization.erpnext_indonesia_localization.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file")
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
	"erpnext_indonesia_localization.erpnext_indonesia_localization.coretax_importer.coretax_importer.read_xlsx_file_from_attached_file",
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
