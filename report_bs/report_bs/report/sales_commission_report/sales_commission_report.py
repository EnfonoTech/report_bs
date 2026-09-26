import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Journal Entry", "fieldname": "journal_entry", "fieldtype": "Link", "options": "Journal Entry", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": "Account", "fieldname": "account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": "Sales Invoice", "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 200},
    ]


def get_data(filters):
    conditions = ["jea.custom_is_commission_account = 1", "je.docstatus = 1"]
    values = {}

    if filters.get("company"):
        conditions.append("je.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("customer"):
        conditions.append("jea.custom_commission_customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("from_date"):
        conditions.append("je.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("je.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    return frappe.db.sql(f"""
        SELECT
            jea.parent AS journal_entry,
            je.posting_date AS posting_date,
            jea.account AS account,
            jea.custom_commission_customer AS customer,
            jea.custom_commission_sales_invoice AS sales_invoice,
            jea.cost_center AS cost_center,
            jea.debit AS debit,
            jea.credit AS credit,
            je.user_remark AS remarks
        FROM `tabJournal Entry Account` jea
        INNER JOIN `tabJournal Entry` je ON je.name = jea.parent
        WHERE {" AND ".join(conditions)}
        ORDER BY je.posting_date DESC
    """, values, as_dict=True)
