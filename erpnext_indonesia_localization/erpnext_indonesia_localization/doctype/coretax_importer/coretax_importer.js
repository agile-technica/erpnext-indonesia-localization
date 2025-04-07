// Copyright (c) 2025, Agile Technica and contributors
// For license information, please see license.txt

frappe.ui.form.on('CoreTax Importer', {
	importer_status: function(frm) {
    	set_import_file_as_read_only_based_on_importer_status(frm);
	},

	onload: function(frm) {
		generate_preview(frm);
		generate_import_log(frm);
        set_import_file_as_read_only_based_on_importer_status(frm);
	},

	refresh: function(frm) {
		hide_start_import_button_based_on_importer_status(frm);
	},

	import_file: function(frm) {
		update_importer_status(frm);
		generate_preview(frm);
	},

	start_import: function(frm) {
	    if (frm.doc.importer_status == "Draft" && frm.doc.import_file){
    	    update_sales_invoice_from_xlsx(frm);
	    }
	}
});

frappe.listview_settings['CoreTax Importer'] = {
	add_fields: ["importer_status"],
	get_indicator: function(doc) {
		if (doc.importer_status == "Update Succeed") {
			return [__("Update Succeed"), "green", "importer_status,=,Succeed"];
		} else if (doc.importer_status == "Update Failed") {
			return [__("Update Failed"), "red", "importer_status,=,Failed"];
		} else if (doc.importer_status == "In Process") {
			return [__("In Process"), "orange", "importer_status,=,In Process"];
		} else {
			return [__("Draft"), "blue", "importer_status,=,Draft"];
		}
	}
}

function set_import_file_as_read_only_based_on_importer_status(frm){
    frm.set_df_property("import_file", "read_only", (frm.doc.importer_status == "In Process" || frm.doc.importer_status == "Succeed") ? 1 : 0);
};


function generate_preview(frm){
	if (frm.doc.import_file){
		frm.set_df_property("coretax_invoice", "hidden", false);
		frm.call("generate_preview", {
            "file": frm.doc.import_file
        }).then(response => {
            if (response.message) {
                frm.set_df_property("coretax_invoice", "options", response.message);
            }
        });
	} else {
		frm.set_df_property("coretax_invoice", "hidden", true);
	}
};

function generate_import_log(frm) {
	if (frm.doc.html) {
		frm.set_df_property("import_log", "options", frm.doc.html);
	} else {
		frm.set_df_property("import_log", "hidden", true);
	}
}

function update_sales_invoice_from_xlsx(frm){
    frm.set_value("importer_status", "In Process");
    frm.save();
    frm.call(
        "start_import", {
        "file": frm.doc.import_file
    });
};



function hide_start_import_button_based_on_importer_status(frm){
	frm.set_df_property("start_import", "hidden", !frm.doc.import_file ? 1 : 0);

	if (frm.doc.importer_status == "In Process" || frm.doc.importer_status == "Update Succeed"){
		frm.set_df_property("start_import", "hidden", 1);
	}
}

function update_importer_status(frm) {
	if (frm.doc.import_file) {
		frm.set_value("importer_status", "Draft");
	} else {
		frm.set_value("importer_status", "");
	}
}
