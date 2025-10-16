//// Copyright (c) 2023, Agile Technica and contributors
//// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
    before_load: function (frm) {
        if (frm.is_new()) {
            frm.doc.tax_invoice_number = undefined;
        }
    },
	taxes_and_charges: function (frm) {
        if(frm.doc.taxes_and_charges){
            set_sales_taxes_template_values(frm, {name: frm.doc.taxes_and_charges});
        };
    },
    onload: function (frm) {
        if (frm.doc.docstatus != 1) {
            set_sales_taxes_template_values(frm, {company: frm.doc.company, is_default: 1});
        }

        clear_coretax_related_fields(frm);
    }
})

function clear_coretax_related_fields(frm) {
	if (frm.doc.amended_from) {
        frm.set_value('is_xml_generated', 0);
        frm.set_value('nomor_faktur_pajak', null);
        frm.set_value('tanggal_faktur_pajak', null);
        frm.set_value('coretax_status', null);
        frm.set_value('coretax_xml_exporter', null);
    }
}

function set_sales_taxes_template_values(frm, filters) {
    frappe.db.get_value('Sales Taxes and Charges Template',
                        filters,
                        ['transaction_code', 'tax_additional_info', 'tax_facility_stamp'])
    .then(r => {
        let values = r.message;
        frm.set_value('transaction_code', values.transaction_code);
        frm.set_value('tax_additional_info', values.tax_additional_info);
        frm.set_value('tax_facility_stamp', values.tax_facility_stamp);
    });
};
