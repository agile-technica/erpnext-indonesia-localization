// Copyright (c) 2022, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Invoice Number Importer', {
    refresh: function (frm) {
        frm.disable_save();
    },
    onload: function(frm) {
        frappe.db.get_single_value('Global Defaults', 'default_company').then((default_company) => {
            if (!frm.doc.company) {
                frm.set_value('company', default_company);
            }
        });
    },
    create_tax_invoice_number: function (frm) {
        frappe.call({
            doc: frm.doc,
            method: 'insert_tax_invoice_number',
            callback: (r) => {
                frappe.msgprint("Importing Tax Invoice Number")

                frm.set_df_property('create_tax_invoice_number', 'hidden', 1);
            }
        })
    },
    from_tax_invoice_number_formatted: function (frm) {
        process_formatted_tax_invoice_number(frm, "from")
    },
    to_tax_invoice_number_formatted: function (frm) {
        process_formatted_tax_invoice_number(frm, "to")
    },
    from_tax_invoice_number: function (frm) {
        process_not_formatted_tax_invoice_number(frm, "from")
    },
    to_tax_invoice_number: function (frm) {
        process_not_formatted_tax_invoice_number(frm, "to")
    }
});

function get_tax_invoice_number_length() {
    let tax_invoice_number_length;

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Indonesia Localization Settings",
        },
        async: false,
        callback(r) {
            if (r.message) {
                tax_invoice_number_length = r.message.tin_length;
            }
        }
    })

    return tax_invoice_number_length;
}

function process_not_formatted_tax_invoice_number(frm, entry) {
    let tax_invoice_number_length = get_tax_invoice_number_length();

    if (frm.doc[`${entry}_tax_invoice_number`].length > tax_invoice_number_length) {
        frappe.throw("Invalid Tax Invoice Number")
    }

    frm.doc[`${entry}_tax_invoice_number_formatted`] = frm.doc[`${entry}_tax_invoice_number`].replace(/(\d{3})(\d{2})(\d{6})/, '$1.$2.$3');
    frm.refresh_field(`${entry}_tax_invoice_number_formatted`);

    if (frm.doc.from_tax_invoice_number && frm.doc.to_tax_invoice_number) {
        frm.doc.tax_invoice_number_total = parseInt(frm.doc.to_tax_invoice_number) - parseInt(frm.doc.from_tax_invoice_number) + 1
        frm.refresh_field("tax_invoice_number_total");
    } else if (frm.doc.from_tax_invoice_number === '' || frm.doc.to_tax_invoice_number === '') {
        frm.doc.tax_invoice_number_total = '0';
        frm.refresh_field("tax_invoice_number_total");
    }
}

function process_formatted_tax_invoice_number(frm, entry) {
    const reg = /\./g;
    let not_formatted_number;
    let tax_invoice_number_length = get_tax_invoice_number_length();

    not_formatted_number = frm.doc[`${entry}_tax_invoice_number_formatted`].replace(reg, "");

    if (not_formatted_number.length > tax_invoice_number_length) {
        frappe.throw("Invalid Tax Invoice Number")
    }

    frm.doc[`${entry}_tax_invoice_number`] = not_formatted_number
    frm.refresh_field(`${entry}_tax_invoice_number`);

    if (frm.doc.from_tax_invoice_number_formatted && frm.doc.to_tax_invoice_number_formatted) {
        frm.doc.tax_invoice_number_total = parseInt(frm.doc.to_tax_invoice_number) - parseInt(frm.doc.from_tax_invoice_number) + 1
        frm.refresh_field("tax_invoice_number_total");
    } else if (frm.doc.from_tax_invoice_number_formatted === '' || frm.doc.to_tax_invoice_number_formatted === '') {
        frm.doc.tax_invoice_number_total = '0';
        frm.refresh_field("tax_invoice_number_total");
    }
}

