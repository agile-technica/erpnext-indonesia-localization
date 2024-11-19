frappe.ui.form.on('Customer Group', {
    kode_pajak: function (frm){
        let kode_pajak = frm.doc.kode_pajak
        let customer_tax_code = kode_pajak.replace(/\D/g, '')
        frm.set_value('customer_tax_code', customer_tax_code)
    }
})