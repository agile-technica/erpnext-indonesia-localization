frappe.ui.form.on('UOM Conversion Detail', {
    custom_tax_uom_code: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        if (child.custom_tax_uom_code) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'CoreTax UnitRef',
                    filters: {code: child.custom_tax_uom_code},
                    fieldname: 'code_description'
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.model.set_value(cdt, cdn, 'custom_tax_uom_description', r.message.code_description);
                    }
                }
            });
        }
    }
});
