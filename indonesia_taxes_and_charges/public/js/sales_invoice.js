//// Copyright (c) 2023, Agile Technica and contributors
//// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
    before_load: function (frm) {
        if (frm.is_new()) {
            frm.doc.tax_invoice_number = undefined;
        }
    }
})
