import pytest
from unittest.mock import patch, MagicMock
from erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter import get_preview_sales_invoice


@patch("frappe.get_value")
@patch("frappe.get_all")
def test_get_preview_sales_invoice_with_data(mock_get_all, mock_get_value):
	# Arrange
	mock_invoices = []
	for i in range(5):
		invoice = MagicMock()
		invoice.name = f"INV-00{i}"
		invoice.posting_date = f"2025-03-{i + 1:02d}"
		invoice.customer = f"CUST-00{i}"
		invoice.grand_total = 1000.0 * (i + 1)
		invoice.total_taxes_and_charges = 100.0 * (i + 1)
		mock_invoices.append(invoice)

	mock_get_all.return_value = mock_invoices
	mock_get_value.side_effect = "Test Company"

	# Act
	result = get_preview_sales_invoice.__wrapped__(
		company="Test Company",
		start_invoice_date="2025-03-01",
		end_invoice_date="2025-03-31",
		branch="Test Branch"
	)

	# Assert
	mock_get_all.assert_called_once_with(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"nomor_faktur_pajak": "",
			"is_xml_generated": 0,
			"company": "Test Company",
			"posting_date": ["between", ["2025-03-01", "2025-03-31"]],
			"taxes_and_charges": ["!=", ""],
			"branch": "Test Branch"
		},
		fields=["name", "posting_date", "customer", "grand_total", "total_taxes_and_charges"],
		order_by='posting_date'
	)

	assert "Showing 5 out of 5 row(s)" in result


@patch("frappe.get_value")
@patch("frappe.get_all")
def test_get_preview_sales_invoice_with_more_than_10_records(mock_get_all, mock_get_value):
	# Arrange
	mock_invoices = []
	for i in range(15):
		invoice = MagicMock()
		invoice.name = f"INV-00{i}"
		invoice.posting_date = f"2025-03-{i + 1:02d}"
		invoice.customer = f"CUST-00{i}"
		invoice.grand_total = 1000.0 * (i + 1)
		invoice.total_taxes_and_charges = 100.0 * (i + 1)
		mock_invoices.append(invoice)

	mock_get_all.return_value = mock_invoices
	mock_get_value.side_effect = "Test Company"

	# Act
	result = get_preview_sales_invoice.__wrapped__(
		company="Test Company",
		start_invoice_date="2025-03-01",
		end_invoice_date="2025-03-31"
	)

	# Assert
	assert "INV-010" not in result
	assert "Showing 10 out of 15 row(s)" in result


@patch("frappe.get_value")
@patch("frappe.get_all")
def test_get_preview_sales_invoice_no_branch_field(mock_get_all, mock_get_value):
	# Arrange
	mock_get_all.return_value = [MagicMock(
		name="INV-001",
		posting_date="2025-03-01",
		customer="CUST-001",
		grand_total=1000.0,
		total_taxes_and_charges=100.0
	)]
	mock_get_value.side_effect = "Test Company"

	# Act
	result = get_preview_sales_invoice.__wrapped__(
		company="Test Company",
		start_invoice_date="2025-03-01",
		end_invoice_date="2025-03-31",
	)

	mock_get_all.assert_called_once_with(
		"Sales Invoice",
		filters={
			"docstatus": 1,
			"nomor_faktur_pajak": "",
			"is_xml_generated": 0,
			"company": "Test Company",
			"posting_date": ["between", ["2025-03-01", "2025-03-31"]],
			"taxes_and_charges": ["!=", ""],
		},
		fields=["name", "posting_date", "customer", "grand_total", "total_taxes_and_charges"],
		order_by='posting_date'
	)

	assert "Showing 1 out of 1 row(s)" in result


@patch("frappe.get_all")
def test_get_preview_sales_invoice_no_data(mock_get_all):
	# Arrange
	mock_get_all.return_value = []

	# Act
	result = get_preview_sales_invoice.__wrapped__(
		company="Test Company",
		start_invoice_date="2025-03-01",
		end_invoice_date="2025-03-31"
	)

	# Assert
	assert result == "<p>No sales invoices found for the selected date range</p>"
