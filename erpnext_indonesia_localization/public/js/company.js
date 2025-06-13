//// Copyright (c) 2025, Agile Technica and contributors
//// For license information, please see license.txt

frappe.ui.form.on('Company', {
    use_company_nitku: function(frm) {
        frm.set_value("companys_nitku", frm.doc.use_company_nitku ? "" : "000000");
    },

	onload: function(frm) {
		frm.add_custom_button(__("Create Indonesia Tax Template"), function() {
			frappe.call({
				method: "erpnext_indonesia_localization.utils.template_tax.create_indonesia_localization_tax_template",
				args: {
					company: frm.doc.name
				},
				callback: function(response) {
					if (response.message) {
						frappe.msgprint(__("Sales Taxes and Charges Template created successfully."), __("Success"));
					} else {
						frappe.msgprint({
							message: __('Sales Taxes and Charges Template already exists.'),
							indicator: 'red',
							title: __('Failed')
						});
					}
				}
			});
		}, __("Manage"))
	},
})
