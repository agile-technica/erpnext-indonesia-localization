frappe.ui.form.on('Customer', {
    tax_id: function(frm) {
        frm.set_df_property('company_address_tax_id', 'reqd', frm.doc.tax_id ? 1 : 0);
    },

	customer_id_type: function (frm) {
		set_customer_id_number_visibility(frm);
	},

	setup: function (frm) {
		auto_fill_tax_country_code_when_setup(frm);
	}
});

function auto_fill_tax_country_code_when_setup(frm) {
	if (frm.doc.coretax_country) {
			frappe.db.get_value("Country", frm.doc.coretax_country, "custom_coretax_countryref")
				.then(r => {
					frm.set_value("tax_country_code", r.message.custom_coretax_countryref);
				})
		}
}

function set_customer_id_number_visibility(frm) {
	if (frm.doc.customer_id_type == "TIN" || frm.doc.customer_id_type == "National ID") {
		frm.set_df_property("customer_id_number", "hidden", 1);
	} else {
		frm.set_df_property("customer_id_number", "hidden", 0);
	}
}
