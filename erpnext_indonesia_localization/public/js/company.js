//// Copyright (c) 2025, Agile Technica and contributors
//// For license information, please see license.txt

frappe.ui.form.on('Company', {
    use_company_nitku: function(frm) {
        frm.set_value("companys_nitku", frm.doc.use_company_nitku ? "" : "000000");
    }
})