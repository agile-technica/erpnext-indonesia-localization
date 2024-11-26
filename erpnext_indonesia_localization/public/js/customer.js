frappe.ui.form.on('Customer', {
    tax_id: function(frm) {
        frm.set_df_property('company_address_tax_id', 'reqd', frm.doc.tax_id ? 1 : 0);
    }
});
