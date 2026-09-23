frappe.listview_settings["Sales Invoice"] = {
    button: {
        show: function (doc) {
            return doc.docstatus === 1;
        },

        get_label: function (doc) {
            let icon_color = "gray";
            let icon_title = "Make Payment";

            if (doc.outstanding_amount == 0) {
                icon_color = "green";
                icon_title = "Full Paid";
            } else if (doc.outstanding_amount < doc.grand_total) {
                icon_color = "orange";
                icon_title = "Partially Paid";
            } else {
                icon_color = "red";
                icon_title = "Unpaid";
            }

            let draft_badge = `<span class="payment-draft-count" 
                                    data-name="${doc.name}"
                                    style="background:#dce0e3; color:#555; border-radius:50%; 
                                           padding:2px 6px; font-size:11px; margin-right:6px; display:none;">
                                    0
                               </span>`;

            let payment_icon = `<i class="fa fa-credit-card" 
                                    style="font-size:14px; color:${icon_color};">
                                 </i>`;

            return draft_badge + payment_icon;
        },

        get_description: function (doc) {
            let icon_title = "Make Payment";

            if (doc.outstanding_amount == 0) {
                icon_title = "Full Paid";
            } else if (doc.outstanding_amount < doc.grand_total) {
                icon_title = "Partially Paid";
            } else {
                icon_title = "Unpaid";
            }

            return __(icon_title);
        },

        action: function (doc) {
            if (doc.outstanding_amount == 0) {
                frappe.msgprint("This invoice is fully paid");
                return;
            }

            frappe.db.get_doc("Sales Invoice", doc.name).then(full_doc => {
                const d = new frappe.ui.Dialog({
                    title: __("Create Payment Entry"),
                    fields: [
                        {
                            fieldname: "paid_amount",
                            label: "Payment Amount",
                            fieldtype: "Currency",
                            reqd: 1,
                            default: full_doc.outstanding_amount
                        },
                        {
                            fieldname: "mode_of_payment",
                            label: "Mode of Payment",
                            fieldtype: "Link",
                            options: "Mode of Payment",
                            reqd: 1,
                            get_query: function () {
                                return {
                                    query: "report_bs.api.mode_of_payment_query",
                                    filters: { company: full_doc.company }
                                };
                            },
                            onchange: function () {
                                let mode = d.get_value("mode_of_payment");

                                if (!mode) return;

                                frappe.db.get_value("Mode of Payment", mode, "type").then(r => {
                                    let is_cash = r.message && r.message.type === "Cash";

                                    d.set_df_property("ref_no", "reqd", is_cash ? 0 : 1);
                                    d.set_df_property("ref_date", "reqd", is_cash ? 0 : 1);
                                    d.set_df_property("ref_no", "hidden", is_cash ? 1 : 0);
                                    d.set_df_property("ref_date", "hidden", is_cash ? 1 : 0);
                                });
                            }
                        },
                        {
                            fieldname: "ref_no",
                            label: "Reference No",
                            fieldtype: "Data",
                            hidden: 1
                        },
                        {
                            fieldname: "ref_date",
                            label: "Reference Date",
                            fieldtype: "Date",
                            hidden: 1
                        }
                    ],

                    primary_action_label: __("Create"),

                    primary_action(values) {
                        frappe.call({
                            method: "report_bs.api.create_payment_entry",
                            args: {
                                sales_invoice: full_doc.name,
                                company: full_doc.company,
                                customer: full_doc.customer,
                                currency: full_doc.currency,
                                outstanding_amount: full_doc.outstanding_amount,
                                paid_amount: values.paid_amount,
                                mode_of_payment: values.mode_of_payment,
                                ref_no: values.ref_no,
                                ref_date: values.ref_date
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.show_alert({
                                        message: __("Draft Payment Entry {0} created", [r.message.name]),
                                        indicator: "green"
                                    });

                                    d.hide();
                                }
                            }
                        });
                    }
                });

                d.show();
            });
        }
    },

    onload(listview) {

        const sidebar = document.querySelector('.layout-side-section');
        if (sidebar) sidebar.style.display = 'none';

        const main_section = document.querySelector('.layout-main-section-wrapper');
        if (main_section) main_section.style.flex = '1';

        this.load_draft_counts(listview);

        // ✅ FIXED: use after_render instead of on_render
        listview.after_render = () => {
            this.load_draft_counts(listview);
        };

        frappe.realtime.on("payment_entry_draft_created", (data) => {

            if (!data || !data.sales_invoice) return;

            const invoice_name = data.sales_invoice;

            const el = $(`.payment-draft-count[data-name='${invoice_name}']`);

            if (el.length) {
                let current = parseInt(el.text()) || 0;
                let new_count = current + 1;

                el.text(new_count);
                el.css({
                    background: "#c4c3c0ff",
                    color: "#000",
                    fontWeight: "bold",
                    display: "inline-block"
                });

                el.attr(
                    "title",
                    `${new_count} draft payment entr${new_count > 1 ? "ies" : "y"} exist`
                );
            }
        });
    },

    load_draft_counts(listview) {

        const invoice_names = [];

        if (listview.data && listview.data.length > 0) {
            listview.data.forEach(doc => {
                if (doc.docstatus === 1) {
                    invoice_names.push(doc.name);
                }
            });
        }

        if (!invoice_names.length) return;

        frappe.call({
            method: "report_bs.api.get_payment_entry_info_bulk",
            args: { invoice_names: invoice_names },
            callback: function (r) {

                if (!r.message) return;

                Object.keys(r.message).forEach(invoice_name => {

                    const drafts = r.message[invoice_name].drafts || 0;
                    const el = $(`.payment-draft-count[data-name='${invoice_name}']`);

                    if (drafts > 0) {
                        el.text(drafts);
                        el.css({
                            background: "#c4c3c0ff",
                            color: "#000",
                            fontWeight: "bold",
                            display: "inline-block"
                        });

                        el.attr(
                            "title",
                            `${drafts} draft payment entr${drafts > 1 ? "ies" : "y"} exist`
                        );
                    } else {
                        el.hide();
                    }
                });
            }
        });
    }
};