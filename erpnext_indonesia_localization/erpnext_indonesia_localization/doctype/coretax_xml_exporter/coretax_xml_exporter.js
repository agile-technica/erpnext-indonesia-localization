// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coretax XML Exporter', {
    onload: function(frm) {
        if(frm.doc.html) {
            frm.set_df_property("sales_invoice_list", "options", frm.doc.html);
        } else {
			frm.set_df_property("sales_invoice_list", "hidden", true);
		}
    },

    refresh: function(frm) {
        if (frm.doc.status == "Failed") {
            toggle_retry_button(frm=frm);
        }
    },

    get_sales_invoice: function(frm) {
        if (frm.doc.start_invoice_date && frm.doc.end_invoice_date && frm.doc.company) {
            frappe.call(
                "erpnext_indonesia_localization.erpnext_indonesia_localization.doctype.coretax_xml_exporter.coretax_xml_exporter.get_preview_sales_invoice",
                {
                    company: frm.doc.company,
                    start_invoice_date: frm.doc.start_invoice_date,
                    end_invoice_date: frm.doc.end_invoice_date,
                    branch: frm.doc.branch
                }
            ).then(r => {
                frm.set_df_property("sales_invoice_list", "hidden", false);
                frm.set_df_property("sales_invoice_list", "options", r.message);
                frm.set_value("html", r.message);
            });
        } else {
            frappe.msgprint("Please select a Company and set a Date Range before proceeding.");
        }
    }
});


function toggle_retry_button(frm){
	frm.add_custom_button(__("Retry"), function() {
        frm.call("export_xml", {}).then(r => {
            if (r.message) {
                frm.set_value("status", r.message);
                frm.save("Update");
            }
        });
    }).css({"color":"black", "background-color": "#e2e2e2"});
}
