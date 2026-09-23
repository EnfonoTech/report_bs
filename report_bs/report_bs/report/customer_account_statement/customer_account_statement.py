import frappe


def execute(filters=None):
    if not filters:
        filters = {}

    # Ensure all required filters are set
    required = ["customer", "from_date", "to_date"]
    for f in required:
        if not filters.get(f):
            frappe.msgprint(f"Please set all filters before running the report.", alert=True)
            return

    # Add required data in filters
    customer = filters.get('customer')
    meta = frappe.get_meta("Customer")
    if meta.has_field("custom_vat_registration_number"):
        customer_vat_no = frappe.db.get_value("Customer", customer, "custom_vat_registration_number")
        filters['customer_vat_no'] = customer_vat_no or None

    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "employee_name")
    filters['created_by'] = employee or user


    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Voucher Type", "fieldname": "voucher_type", "fieldtype": "Data", "width": 150},
        {"label": "Voucher No", "fieldname": "voucher_no", "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 180},
        {"label": "Against Voucher", "fieldname": "against_voucher", "fieldtype": "Dynamic Link", "options": "against_voucher_type", "width": 180},
        {"label": "Debit", "fieldname": "debit", "fieldtype": "Currency", "width": 120},
        {"label": "Credit", "fieldname": "credit", "fieldtype": "Currency", "width": 120},
        {"label": "Balance", "fieldname": "balance", "fieldtype": "Currency", "width": 120},
    ]


def get_system_generated_cr_dr_notes():
    """Journal Entries for system generated Credit/Debit Notes"""
    return frappe.get_all(
        "Journal Entry",
        filters={
            "docstatus": 1,
            "voucher_type": ["in", ["Credit Note", "Debit Note"]],
            "is_system_generated": 1,
        },
        pluck="name",
    )


def get_data(filters):
    voucher_no_not_in = None
    if filters.get("ignore_cr_dr_notes"):
        voucher_no_not_in = get_system_generated_cr_dr_notes()

    # Fetch opening balance before from_date
    opening_balance = get_opening_balance(filters, voucher_no_not_in)

    conditions = [
        "party_type = 'Customer'",
        "party = %(customer)s",
        "posting_date >= %(from_date)s",
        "posting_date <= %(to_date)s"
    ]

    values = {
        "customer": filters["customer"],
        "from_date": filters["from_date"],
        "to_date": filters["to_date"],
    }

    if voucher_no_not_in:
        conditions.append("voucher_no NOT IN %(voucher_no_not_in)s")
        values["voucher_no_not_in"] = voucher_no_not_in

    gl_entries = frappe.db.sql(f"""
        SELECT
            posting_date,
            voucher_type,
            voucher_subtype,
            voucher_no,
            against_voucher_type,
            against_voucher,
            debit,
            credit
        FROM
            `tabGL Entry`
        WHERE
            {" AND ".join(conditions)}
        ORDER BY posting_date, creation
    """, values, as_dict=True)

    data = []

    # Add opening balance row
    data.append({
        "posting_date": None,
        "voucher_type": "Opening Balance",
        "voucher_subtype": "",
        "voucher_no": "",
        "against_voucher": "",
        "debit": 0,
        "credit": 0,
        "balance": opening_balance
    })

    balance = opening_balance
    credit_sum = 0
    debit_sum = 0
    credit_notes = 0

    for d in gl_entries:
        balance += d.debit - d.credit
        debit_sum += d.debit
        if d.voucher_subtype == d.against_voucher_type:
            d.against_voucher = None
        if d.voucher_subtype == "Credit Note":
            d.voucher_type = "Credit Note"
            credit_notes += d.credit
        if d.voucher_type == "Payment Entry":
            credit_sum += d.credit
        d.balance = balance
        data.append(d)

    # Add closing balance row
    data.append({
        "posting_date": None,
        "voucher_type": "Closing Balance",
        "voucher_subtype": "",
        "voucher_no": "",
        "against_voucher": "",
        "debit": None,
        "credit": None,
        "balance": data[len(data) - 1].get("balance", 0)
    })

    # add required data as last row of the table
    data.append({
        "customer_vat_no": filters.get('customer_vat_no'),
        "created_by": filters['created_by'],
        "statement_date": frappe.utils.today(),
        "credit_sum": credit_sum,
        "debit_sum": debit_sum,
        "credit_notes": credit_notes,
        "debit": None,
        "credit": None,
        "balance": None
    })

    
    return data


def get_opening_balance(filters, voucher_no_not_in=None):
    """Compute opening balance before from_date."""
    conditions = [
        "party_type = 'Customer'",
        "party = %(customer)s",
        "posting_date < %(from_date)s"
    ]

    values = {"customer": filters["customer"], "from_date": filters["from_date"]}

    if voucher_no_not_in:
        conditions.append("voucher_no NOT IN %(voucher_no_not_in)s")
        values["voucher_no_not_in"] = voucher_no_not_in

    result = frappe.db.sql(f"""
        SELECT
            SUM(debit) - SUM(credit) AS balance
        FROM
            `tabGL Entry`
        WHERE
            {" AND ".join(conditions)}
    """, values, as_dict=True)

    return result[0].balance or 0