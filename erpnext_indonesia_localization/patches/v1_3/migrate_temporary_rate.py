import frappe


def execute():
	if not frappe.db.has_column("Sales Taxes and Charges", "old_temporary_rate"):
		return

	sales_taxes_and_charges_docs = frappe.get_all("Sales Taxes and Charges", fields=["old_temporary_rate", "name"])

	for charge in sales_taxes_and_charges_docs:
		frappe.db.set_value("Sales Taxes and Charges", charge.name, "temporary_rate", charge.old_temporary_rate)

	frappe.clear_cache(doctype="Sales Taxes and Charges")
