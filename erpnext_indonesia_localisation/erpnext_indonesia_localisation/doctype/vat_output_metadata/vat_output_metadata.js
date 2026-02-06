// Copyright (c) 2023, Agile Technica and contributors
// For license information, please see license.txt
function append_call_pajakio_api_button(frm){
    frm.add_custom_button(__('Call Pajak.io API'), function() {
        frappe.confirm(
            'Proceed to create a VAT Output?',
            function(){
                frappe.call({
                    method: 'erpnext_indonesia_localisation.erpnext_indonesia_localisation.api.pajakio.create_vat_output_js',
                    args: {
                        name: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.show_alert(r.message, 5);
                        }
                    }
                });
            },
            function(){
            }
        )
    });
}

function append_download_pdf_button(frm){
    frm.add_custom_button(__('Download PDF'), function() {
        frappe.confirm(
            'Proceed to download PDF?',
            function(){
                window.open('/api/method/erpnext_indonesia_localisation.erpnext_indonesia_localisation.doctype.vat_output_metadata.vat_output_metadata.convert_base64_to_pdf?docname=' + frm.doc.name, '_blank');
            },
            function(){
            }
        )
    });
}

function append_upload_vat_button(frm){
    frm.add_custom_button(__('Upload VAT'), function() {
        frappe.confirm(
            'Proceed to upload VAT?',
            function(){
                frappe.call({
                    method: 'erpnext_indonesia_localisation.erpnext_indonesia_localisation.api.pajakio.upload_vat_output',
                    args: {
                        doc: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.show_alert(r.message, 5);
                        }
                    }
                });
            },
            function(){
            }
        )
    });
}

frappe.ui.form.on('VAT Output Metadata', {
	 refresh: function(frm) {
	    if (frm.doc.docstatus === 0){
	        append_call_pajakio_api_button(frm);
	    }
        if (frm.doc.transactionid && frm.doc.vat_upload_success === 0) {
            append_upload_vat_button(frm);
        }
        if (frm.doc.base64) {
            append_download_pdf_button(frm);
        }
	 }
});
