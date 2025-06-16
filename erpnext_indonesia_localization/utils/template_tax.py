import frappe
from frappe.utils import now

@frappe.whitelist()
def create_indonesia_localization_tax_template(company):
	"""
	Create a tax template for CoreTax if it does not already exist.
	"""
	abbr = frappe.db.get_value("Company", company, "abbr")
	tax_template_12 = frappe.db.exists("Sales Taxes and Charges Template", f"PPN Penjualan 12% - {abbr}")
	tax_template_11 = frappe.db.exists("Sales Taxes and Charges Template", f"PPN Penjualan 11% - {abbr}")

	if not tax_template_12 and not tax_template_11:
		tax_tamplate_json = [
			{
				"company": company,
				"title": "PPN Penjualan 12%",
				"disabled": 0,
				"is_default": 0,
				"name": f"PPN Penjualan 12% - {abbr}",
				"tax_category": None,
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
						"parent": f"PPN Penjualan 12% - {abbr}",
						"parentfield": "taxes",
						"parenttype": "Sales Taxes and Charges Template",
						"use_temporary_rate": True,
						"rate": 11.0,
						"temporary_rate": 12,
						"row_id": None,
						"tax_amount": 0.0,
						"tax_amount_after_discount_amount": 0.0,
						"total": 0.0
					}
				]
			},
			{
				"company": company,
				"title": "PPN Penjualan 11%",
				"disabled": 0,
				"is_default": 0,
				"name": f"PPN Penjualan 11% - {abbr}",
				"tax_category": None,
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
						"parent": f"PPN Penjualan 12% - {abbr}",
						"parentfield": "taxes",
						"parenttype": "Sales Taxes and Charges Template",
						"rate": 11.0,
						"row_id": None,
						"tax_amount": 0.0,
						"tax_amount_after_discount_amount": 0.0,
						"total": 0.0
					}
				],
			}
		]

		for tax_template in tax_tamplate_json:
			frappe.get_doc({
				'doctype': 'Sales Taxes and Charges Template',
				'company': tax_template['company'],
				'disabled': tax_template['disabled'],
				'is_default': tax_template['is_default'],
				'name': tax_template['name'],
				'tax_category': tax_template['tax_category'],
				'taxes': tax_template['taxes'],
				'title': tax_template['title'],
				'creation': now(),
				'modified': now()
			}).insert()

		return True
