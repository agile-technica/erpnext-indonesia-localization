// Copyright (c) 2022, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Invoice Number', {
    refresh: function (frm) {
        if (frm.doc.linked_si) {
            frm.add_custom_button(__("Unlink Tax Invoice Number"), function () {
                frappe.confirm(__('Are you sure you want to <b>unlink this Tax Invoice Number</b>?'), function () {
                    frappe.call({
                        method: "erpnext_indonesia_localisation.erpnext_indonesia_localisation.doctype.tax_invoice_number.tax_invoice_number.unlink_tax_invoice_number",
                        args: {
                            tax_invoice_number: frm.doc.name
                        },
                    })
                        .then(() => {
                            frm.reload_doc();
                        });
                });
            });
        }
    }
});
