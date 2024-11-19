// Copyright (c) 2022, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tax Invoice Exporter', {
    refresh: function (frm) {
        if (!frm.is_loading_filling_si) {
            frm.fields_dict.get_sales_invoices.set_description("")
        }

        if (frm.is_new()) {
            clear_si_table(frm)
        }

        if (!(frm.is_new())) {
            validate_tin_availability(frm)
        }

        frm.refresh_field("sales_invoices")
        frm.trigger("customer_type")
    },
    on_submit: function(frm) {
        frm.refresh_field("sales_invoices")
    },
    company: function (frm) {
        clear_si_table(frm)
        validate_tin_availability(frm)
    },
    si_posting_date: function (frm) {
        clear_si_table(frm)
    },
    get_sales_invoices: function (frm) {
        clear_si_table(frm)

        frappe.call({
            doc: frm.doc,
            method: 'fill_sales_invoices',
            args: {
                "is_single_tax_invoice_number": frm.doc.assign_tax_invoice_number_to_multiple_invoices
            },
            callback: (r) => {
                if (r.message) {
                    frm.fields_dict.get_sales_invoices.set_description("")
                    frm.clear_table('sales_invoices')

                    for (let si_detail of r.message) {
                        frm.add_child("sales_invoices",
                            {
                                sales_invoice: si_detail['sales_invoice'],
                                delivery_note: si_detail['delivery_note'],
                                tax_invoice_number: si_detail['tax_invoice_number'],
                                total_amount: si_detail['total_amount'],
                                sales_invoice_date: si_detail['sales_invoice_date'],
                                customer: si_detail['customer'],
                                customer_name: si_detail['customer_name'],
                                branch: si_detail['branch']
                            })
                        frm.refresh_field("sales_invoices")
                    }
                }
            }
        })
    },
    link_tin_to_si: function (frm) {
        frappe.msgprint("Starting Link Tax Invoice Number to Sales Invoice")

        frappe.call({
            doc: frm.doc,
            method: 'update_tin_with_si',
            args: {
                "event_trigger": "submit"
            },
            callback: (r) => {
                if (r.message) {
                    if (r.message.error) {
                        frappe.throw(__(r.message.error))
                    }
                }
            }
        })
    },
    export_as_csv: function (frm) {
        frm.refresh_field("sales_invoices")
        frappe.call({
            doc: frm.doc,
            method: 'enqueue_export_as_csv',
            callback: (r) => {
                frm.reload_doc()

                let modal = frappe.msgprint({
                    title: __('Notification'),
                    message: __('Starting Export to CSV'),
                    primary_action: {
                        action(values) {
                            cur_dialog.hide()
                        }
                    }
                })
                modal.get_close_btn().hide()
            }
        })
    },
    customer_type: function(frm) {
        if(frm.doc.customer_type == 'Non PKP') {
            frm.set_df_property('assign_tax_invoice_number_to_multiple_invoices', 'hidden', 0)
        }else{
            frm.set_value('assign_tax_invoice_number_to_multiple_invoices', 0);
            frm.set_df_property('assign_tax_invoice_number_to_multiple_invoices', 'hidden', 1);
        }
    }
})

function clear_si_table(frm) {
    frm.clear_table('sales_invoices')
    frm.refresh_field("sales_invoices")
}

function validate_tin_availability(frm) {
    if (frm.doc.company && frm.doc.docstatus == 0) {
        frappe.db.get_value('Indonesia Localization Settings', 'Indonesia Localization Settings', 'minimum_tin_threshold')
            .then(r => {
                frappe.db.get_list('Tax Invoice Number', {
                    fields: ['name', 'status'],
                    filters: {
                        status: 'Available',
                        company: frm.doc.company
                    },
                    limit: r.message.minimum_tin_threshold + 1
                }).then(records => {
                    if (records.length < r.message.minimum_tin_threshold) {
                        let error_msg = __(`Company ${frm.doc.company} has ${records.length} Tax Invoice Number left. `)

                        frappe.msgprint(error_msg.concat(__(`Please import new Tax Invoice Number`)))
                    }
                })
            })
    }
}

