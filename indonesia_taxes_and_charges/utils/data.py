# -*- coding: utf-8 -*-
# Copyright (c) 2022, Agile Technica and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import math
import frappe


def cint(s, default=0):
	try:
		if float(s) % 1 >= 0.5:
			return math.ceil(float(s))
		elif float(s) % 1 < 0.5:
			return math.floor(float(s))
	except Exception:
		return default


def get_tax_prefix_code(si_doc):
	itc_settings = frappe.get_single("ITC Settings")

	for prefix in itc_settings.tax_prefix_codes:
		if si_doc.taxes_and_charges == prefix.sales_taxes_and_charges_template:
			if prefix.tax_prefix_code == '030' and itc_settings.use_min_grand_total_for_wapu:
				if si_doc.grand_total < itc_settings.min_grand_total_for_wapu:
					prefix.tax_prefix_code = '010'

			if itc_settings.use_amended_from_as_tin_revision_flag and si_doc.amended_from:
				old_si_doc = frappe.get_doc("Sales Invoice", si_doc.amended_from)
				if old_si_doc.tax_invoice_number:
					prefix.tax_prefix_code = prefix.tax_prefix_code[:2] + '1'

			elif itc_settings.tin_revision_if_only_si_had_tin_before:
				if si_doc.custom_si_had_tin_before:
					prefix.tax_prefix_code = prefix.tax_prefix_code[:2] + '1'

			return prefix.tax_prefix_code
