// Copyright (c) 2025, aravind@enfono.com and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Account Statement"] = {
    "filters": [
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "ignore_cr_dr_notes",
            "label": __("Ignore System Generated Credit / Debit Notes"),
            "fieldtype": "Check",
            "default": 0
        }
    ],
    onload: function (report) {
        report.page.add_inner_button(__("Reset Filters"), function() {
            const today = frappe.datetime.get_today();
            const month_start = frappe.datetime.month_start(today);

            report.set_filter_value("customer", null);
            report.set_filter_value("from_date", null);
            report.set_filter_value("to_date", null);
            report.set_filter_value("ignore_cr_dr_notes", 0);
            report.refresh();
        });
    }
};

