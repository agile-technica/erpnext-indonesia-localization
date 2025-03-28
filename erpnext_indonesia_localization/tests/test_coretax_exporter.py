import pytest
from unittest.mock import patch, MagicMock
from erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter import get_preview_sales_invoice
from erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter import CoretaxXMLExporter


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


@patch("frappe.throw")
@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.fetch_sales_invoices")
def test_export_xml_no_invoices(mock_fetch_sales_invoice, mock_frappe_throw):
	# Arrange
	mock_fetch_sales_invoice.return_value = ([], {})
	doc = MagicMock()

	# Act
	result = CoretaxXMLExporter.export_xml.__wrapped__(doc)

	# Assert
	mock_frappe_throw.assert_called_once_with("Sales Invoices is Not Found. Please fetch the latest data.")


@patch("frappe.enqueue")
@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.fetch_sales_invoices")
def test_export_xml_with_more_than_500_invoices(mock_fetch_sales_invoice, mock_frappe_enqueue):
	# Assign
	invoice_docs = [MagicMock() for _ in range(501)]
	company_doc = MagicMock()
	doc = MagicMock()
	mock_fetch_sales_invoice.return_value = (invoice_docs, company_doc)

	# Act
	result = CoretaxXMLExporter.export_xml.__wrapped__(doc)

	# Assert
	mock_frappe_enqueue.assert_called_once()


@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.export_xml")
@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.fetch_sales_invoices")
def test_export_xml_with_successful_export(mock_fetch_sales_invoice, mock_export_xml):
	# Assign
	invoice_docs = ["test" for _ in range(3)]
	company_doc = MagicMock()
	doc = MagicMock()
	doc.status = ""
	mock_fetch_sales_invoice.return_value = (invoice_docs, company_doc)
	mock_export_xml.return_value = "Succeed"

	# Act
	result = CoretaxXMLExporter.export_xml.__wrapped__(doc)

	# Assert
	mock_export_xml.assert_called_once()
	assert result == "Succeed"
	assert doc.status == "Succeed"


@patch("frappe.throw")
@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.export_xml")
@patch("indonesia_taxes_and_charges.indonesia_taxes_and_charges.doctype.coretax_xml_exporter.coretax_xml_exporter.fetch_sales_invoices")
def test_export_xml_with_failed_export(mock_fetch_sales_invoice, mock_export_xml, mock_frappe_throw):
	# Assign
	invoice_docs = ["test" for _ in range(3)]
	company_doc = MagicMock()
	doc = MagicMock()
	doc.status = ""
	mock_fetch_sales_invoice.return_value = (invoice_docs, company_doc)
	mock_export_xml.return_value = "Failed"

	# Act
	result = CoretaxXMLExporter.export_xml.__wrapped__(doc)

	# Assert
	assert doc.status == "Failed"
	mock_frappe_throw.assert_called_once_with("Exporting XML Failed")
