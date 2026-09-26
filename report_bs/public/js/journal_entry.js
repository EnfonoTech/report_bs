frappe.ui.form.on("Journal Entry Account", {
    custom_commission_customer: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, "custom_commission_sales_invoice", null);
    }
});

frappe.ui.form.on("Journal Entry", {
    setup: function (frm) {
        frm.set_query("custom_commission_sales_invoice", "accounts", function (doc, cdt, cdn) {
            var row = locals[cdt][cdn];
            return {
                filters: [
                    ["Sales Invoice", "docstatus", "=", 1],
                    ["Sales Invoice", "customer", "=", row.custom_commission_customer]
                ]
            };
        });
    }
});
