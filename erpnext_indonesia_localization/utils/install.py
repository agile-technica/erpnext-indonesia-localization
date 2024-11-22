import frappe
from frappe.utils import now

def init_setup_eil():
	create_sales_taxes_and_charges_templates()

def create_sales_taxes_and_charges_templates():
	"""
	Create Sales Taxes and Charges Templates with default company from global settings.
	:return:
	"""

	global_defaults = frappe.get_single("Global Defaults")
	default_company = global_defaults.default_company
	company_doc = frappe.get_doc("Company", default_company)

	data_json = [
		{
			"company": default_company,
			"title": "PPN Penjualan 12%",
			"disabled": 0,
			"is_default": 0,
			"name": f"PPN Penjualan 12% - {company_doc.abbr}",
			"tax_category": None,
			"taxes": [
				{
					"account_currency": "IDR",
					"account_head": f"2141.000 - Hutang Pajak - {company_doc.abbr}",
					"base_tax_amount": 0.0,
					"base_tax_amount_after_discount_amount": 0.0,
					"base_total": 0.0,
					"charge_type": "On Net Total",
					"cost_center": f"Main - {company_doc.abbr}",
					"description": "Hutang Pajak",
					"dont_recompute_tax": 0,
					"included_in_paid_amount": 0,
					"included_in_print_rate": 0,
					"item_wise_tax_detail": None,
					"parent": f"PPN Penjualan 12% - {company_doc.abbr}",
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
			"company": default_company,
			"title": "PPN Penjualan 11%",
			"disabled": 0,
			"is_default": 0,
			"name": f"PPN Penjualan 11% - {company_doc.abbr}",
			"tax_category": None,
			"taxes": [
				{
					"account_currency": "IDR",
					"account_head": f"2141.000 - Hutang Pajak - {company_doc.abbr}",
					"base_tax_amount": 0.0,
					"base_tax_amount_after_discount_amount": 0.0,
					"base_total": 0.0,
					"charge_type": "On Net Total",
					"cost_center": f"Main - {company_doc.abbr}",
					"description": "Hutang Pajak",
					"dont_recompute_tax": 0,
					"included_in_paid_amount": 0,
					"included_in_print_rate": 0,
					"item_wise_tax_detail": None,
					"parent": f"PPN Penjualan 12% - {company_doc.abbr}",
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

	for item in data_json:
		if not frappe.db.exists("Sales Taxes and Charges Template", item['name']):
			tax_template = frappe.get_doc({
				'doctype': 'Sales Taxes and Charges Template',
				'company': item['company'],
				'disabled': item['disabled'],
				'is_default': item['is_default'],
				'name': item['name'],
				'tax_category': item['tax_category'],
				'taxes': item['taxes'],
				'title': item['title'],
				'creation': now(),
				'modified': now(),
				'owner': 'Administrator',
				'modified_by': 'Administrator',
			})
			tax_template.insert()
			frappe.db.commit()
			print(f"Sales Taxes and Charges Template '{item['name']}' created successfully.")
		else:
			print(f"Sales Taxes and Charges Template '{item['name']}' already exists!!!")