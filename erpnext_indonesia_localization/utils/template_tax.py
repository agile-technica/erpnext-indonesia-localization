import frappe
from frappe.utils import now

@frappe.whitelist()
def create_indonesia_localization_tax_template(company):
	abbr = frappe.db.get_value("Company", company, "abbr")
	created_template = []

	if not frappe.db.exists("Sales Taxes and Charges Template", f"PPN Penjualan 12% - {abbr}"):
		created_template.append(create_tax_template(company, abbr, 12))

	if not frappe.db.exists("Sales Taxes and Charges Template", f"PPN Penjualan 11% - {abbr}"):
		created_template.append(create_tax_template(company, abbr, 11))

	return created_template if created_template else None


def create_tax_template(company, abbr, rate):
	if not company or not abbr or not rate:
		frappe.throw("Please provide company, abbreviation, and rate.")

	template_tax = frappe.get_doc({
		"doctype": "Sales Taxes and Charges Template",
		"company": company,
        "title": f"PPN Penjualan {rate}%",
        "disabled": 0,
        "is_default": 0,
        "name": f"PPN Penjualan {rate}% - {abbr}",
        "tax_category": None,
        "creation": now(),
		"modified": now(),
        "taxes": [
            {
                "account_currency": "IDR",
                "account_head": f"VAT - {abbr}",
                "base_tax_amount": 0.0,
                "base_tax_amount_after_discount_amount": 0.0,
                "base_total": 0.0,
                "charge_type": "On Net Total",
                "cost_center": f"Main - {abbr}",
                "description": "Hutang Pajak",
                "dont_recompute_tax": 0,
                "included_in_paid_amount": 0,
                "included_in_print_rate": 0,
                "item_wise_tax_detail": None,
                "parent": f"PPN Penjualan {rate}% - {abbr}",
                "parentfield": "taxes",
                "parenttype": "Sales Taxes and Charges Template",
                "use_temporary_rate": True if rate == 12 else False,
                "rate": 11,
                "temporary_rate": 12 if rate == 12 else 0,
                "row_id": None,
                "tax_amount": 0.0,
                "tax_amount_after_discount_amount": 0.0,
                "total": 0.0
            }
        ]
	})

	template_tax.insert()
	return template_tax.name
