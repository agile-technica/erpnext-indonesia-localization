import frappe
from frappe.utils import now

def init_setup_eil():
	create_sales_taxes_and_charges_templates()

def create_sales_taxes_and_charges_templates():
	"""
	Create Sales Taxes and Charges Templates with default company from global settings.
	:return:
	"""

	default_company = frappe.db.get_single_value("Global Defaults", "default_company")

	if not default_company:
		return

	company = frappe.get_value("Company", default_company, ["name", "abbr"], as_dict=True)

	tax_tamplate_json = [
		{
			"company": company.name,
			"title": "PPN Penjualan 12%",
			"disabled": 0,
			"is_default": 0,
			"name": f"PPN Penjualan 12% - {company.abbr}",
			"tax_category": None,
			"taxes": [
				{
					"account_currency": "IDR",
					"account_head": f"2141.000 - Hutang Pajak - {company.abbr}",
					"base_tax_amount": 0.0,
					"base_tax_amount_after_discount_amount": 0.0,
					"base_total": 0.0,
					"charge_type": "On Net Total",
					"cost_center": f"Main - {company.abbr}",
					"description": "Hutang Pajak",
					"dont_recompute_tax": 0,
					"included_in_paid_amount": 0,
					"included_in_print_rate": 0,
					"item_wise_tax_detail": None,
					"parent": f"PPN Penjualan 12% - {company.abbr}",
					"parentfield": "taxes",
					"parenttype": "Sales Taxes and Charges Template",
					"rate": 12.0,
					"row_id": None,
					"tax_amount": 0.0,
					"tax_amount_after_discount_amount": 0.0,
					"total": 0.0
				}
			]
		},
		{
			"company": company.name,
			"title": "PPN Penjualan 11%",
			"disabled": 0,
			"is_default": 0,
			"name": f"PPN Penjualan 11% - {company.abbr}",
			"tax_category": None,
			"taxes": [
				{
					"account_currency": "IDR",
					"account_head": f"2141.000 - Hutang Pajak - {company.abbr}",
					"base_tax_amount": 0.0,
					"base_tax_amount_after_discount_amount": 0.0,
					"base_total": 0.0,
					"charge_type": "On Net Total",
					"cost_center": f"Main - {company.abbr}",
					"description": "Hutang Pajak",
					"dont_recompute_tax": 0,
					"included_in_paid_amount": 0,
					"included_in_print_rate": 0,
					"item_wise_tax_detail": None,
					"parent": f"PPN Penjualan 12% - {company.abbr}",
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

	for item in tax_tamplate_json:
		if not frappe.db.exists("Sales Taxes and Charges Template", item['name']):
			frappe.get_doc({
				'doctype': 'Sales Taxes and Charges Template',
				'company': item['company'],
				'disabled': item['disabled'],
				'is_default': item['is_default'],
				'name': item['name'],
				'tax_category': item['tax_category'],
				'taxes': item['taxes'],
				'title': item['title'],
				'creation': now(),
				'modified': now()
			}).insert()

			print(f"Sales Taxes and Charges Template '{item['name']}' created successfully.")
		else:
			print(f"Sales Taxes and Charges Template '{item['name']}' already exists!!!")