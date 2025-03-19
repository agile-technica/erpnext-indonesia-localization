frappe.ui.form.on('Customer', {
    tax_id: function(frm) {
        frm.set_df_property('company_address_tax_id', 'reqd', frm.doc.tax_id ? 1 : 0);
    },

	customer_id_type: function (frm) {
		if (frm.doc.customer_id_type == "TIN") {
			frm.set_df_property("customer_id_number", "hidden", 1);
		} else {
			frm.set_df_property("customer_id_number", "hidden", 0);
		}
	},

	setup: function (frm) {
		if (frm.doc.coretax_country) {
			frappe.db.get_value("Country", frm.doc.coretax_country, "custom_coretax_countryref")
				.then(r => {
					frm.set_value("tax_country_code", r.message.custom_coretax_countryref);
				})
		}
	}
});
