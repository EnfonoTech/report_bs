import frappe
import json

def update_invoice_status(doc, method=None):
    if doc.outstanding_amount == 0:
        status = "Paid"
    elif doc.outstanding_amount == doc.grand_total:
        status = "Unpaid"
    else:
        status = "Partially Paid"
    frappe.db.set_value("Sales Invoice", doc.name, "custom_invoice_status", status)

def update_linked_invoices_status(doc, method=None):
    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice" and ref.reference_name:
            inv = frappe.get_doc("Sales Invoice", ref.reference_name)
            update_invoice_status(inv)

@frappe.whitelist()
def create_payment_entry(sales_invoice, company, customer, currency, outstanding_amount, paid_amount, mode_of_payment, ref_no=None, ref_date=None):
    # Convert numeric inputs safely
    try:
        paid_amount = float(paid_amount)
        outstanding_amount = float(outstanding_amount)
    except (TypeError, ValueError):
        frappe.throw("Invalid numeric value for Paid Amount or Outstanding Amount")

    # Step 1: Find account for given Mode of Payment + Company
    account_row = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": mode_of_payment, "company": company},
        ["default_account"],
        as_dict=True
    )

    if not account_row or not account_row.default_account:
        frappe.throw(f"No default account found for Mode of Payment '{mode_of_payment}' in company '{company}'")

    paid_to_account = account_row.default_account

    # Step 2: Get account currency
    paid_to_currency = frappe.db.get_value("Account", paid_to_account, "account_currency") or currency

    # Step 3: Build Payment Entry document
    payment_entry = frappe.new_doc("Payment Entry")
    payment_entry.payment_type = "Receive"
    payment_entry.party_type = "Customer"
    payment_entry.party = customer
    payment_entry.posting_date = frappe.utils.today()
    payment_entry.company = company
    payment_entry.currency = currency
    payment_entry.source_exchange_rate = 1
    payment_entry.target_exchange_rate = 1
    payment_entry.paid_amount = paid_amount
    payment_entry.received_amount = paid_amount
    payment_entry.mode_of_payment = mode_of_payment
    payment_entry.paid_to = paid_to_account
    payment_entry.paid_to_account_currency = paid_to_currency
    payment_entry.reference_no = ref_no
    payment_entry.reference_date = ref_date
    payment_entry.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": sales_invoice,
        "allocated_amount": paid_amount
    })

    # Step 4: Save as draft (ignore permission)
    payment_entry.insert(ignore_permissions=True)

    return {"name": payment_entry.name}

@frappe.whitelist()
def mode_of_payment_query(doctype, txt, searchfield, start, page_len, filters):
    """Only show Mode of Payment records that have an account linked for the given company"""
    company = filters.get("company") if filters else None

    if not company:
        return []

    return frappe.db.sql("""
        SELECT mop.name
        FROM `tabMode of Payment` mop
        INNER JOIN `tabMode of Payment Account` mopa ON mopa.parent = mop.name
        WHERE mopa.company = %(company)s
            AND mop.name LIKE %(txt)s
        ORDER BY mop.name
        LIMIT %(page_len)s OFFSET %(start)s
    """, {
        "company": company,
        "txt": "%{}%".format(txt),
        "start": frappe.utils.cint(start),
        "page_len": frappe.utils.cint(page_len)
    })

@frappe.whitelist()
def get_payment_entry_info(invoice_name):
    """Return count of payment entries (and drafts) linked to a Sales Invoice"""
    try:
        # Get all Payment Entries linked to this Sales Invoice
        refs = frappe.get_all(
            "Payment Entry Reference",
            filters={
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_name
            },
            fields=["parent"]
        )

        if not refs:
            return {"total": 0, "drafts": 0}

        payment_names = [r.parent for r in refs]

        # Get their docstatus
        entries = frappe.get_all(
            "Payment Entry",
            filters={"name": ["in", payment_names]},
            fields=["name", "docstatus"],
            ignore_permissions=True
        )

        total = len(entries)
        drafts = len([e for e in entries if e.docstatus == 0])

        return {"total": total, "drafts": drafts}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Payment Entry Info Error")
        return {"total": 0, "drafts": 0}

@frappe.whitelist()
def get_payment_entry_info_bulk(invoice_names):
    """Get draft payment entry counts for multiple invoices"""

    if isinstance(invoice_names, str):
        invoice_names = json.loads(invoice_names)

    if not invoice_names:
        return {}

    result = {name: {"drafts": 0} for name in invoice_names}

    draft_counts = frappe.db.sql("""
        SELECT 
            per.reference_name,
            COUNT(pe.name) as count
        FROM `tabPayment Entry Reference` per
        INNER JOIN `tabPayment Entry` pe
            ON pe.name = per.parent
        WHERE 
            per.reference_doctype = 'Sales Invoice'
            AND per.reference_name IN %(invoice_names)s
            AND pe.docstatus = 0
        GROUP BY per.reference_name
    """, {
        "invoice_names": tuple(invoice_names)
    }, as_dict=True)

    for row in draft_counts:
        result[row.reference_name]["drafts"] = row.count

    return result
