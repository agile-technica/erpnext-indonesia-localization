   frappe.ui.form.on('Customer', {
       tax_id: function(frm) {
           if (frm.doc.tax_id) {
               frm.set_df_property('company_address_tax_id', 'reqd', 1);
           } else {
               frm.set_df_property('company_address_tax_id', 'reqd', 0);
           }
       }
   });
