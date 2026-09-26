app_name = "report_bs"
app_title = "Report BS"
app_publisher = "aravind@enfono.com"
app_description = "Custom Reports"
app_email = "aravind@enfono.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "report_bs",
# 		"logo": "/assets/report_bs/logo.png",
# 		"title": "Report BS",
# 		"route": "/report_bs",
# 		"has_permission": "report_bs.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/report_bs/css/report_bs.css"
# app_include_js = "/assets/report_bs/js/report_bs.js"

# include js, css files in header of web template
# web_include_css = "/assets/report_bs/css/report_bs.css"
# web_include_js = "/assets/report_bs/js/report_bs.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "report_bs/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Payment Entry" : "public/js/payment_entry.js",
    "Journal Entry" : "public/js/journal_entry.js"
}
doctype_list_js = {"Sales Invoice": "public/js/sales_invoice_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "report_bs/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "report_bs.utils.jinja_methods",
# 	"filters": "report_bs.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "report_bs.install.before_install"
# after_install = "report_bs.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "report_bs.uninstall.before_uninstall"
# after_uninstall = "report_bs.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "report_bs.utils.before_app_install"
# after_app_install = "report_bs.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "report_bs.utils.before_app_uninstall"
# after_app_uninstall = "report_bs.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "report_bs.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Payment Entry": {
        "after_insert": "report_bs.payment_entry.after_insert"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"report_bs.tasks.all"
# 	],
# 	"daily": [
# 		"report_bs.tasks.daily"
# 	],
# 	"hourly": [
# 		"report_bs.tasks.hourly"
# 	],
# 	"weekly": [
# 		"report_bs.tasks.weekly"
# 	],
# 	"monthly": [
# 		"report_bs.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "report_bs.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "report_bs.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "report_bs.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["report_bs.utils.before_request"]
# after_request = ["report_bs.utils.after_request"]

# Job Events
# ----------
# before_job = ["report_bs.utils.before_job"]
# after_job = ["report_bs.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"report_bs.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
                "Payment Entry-custom_round_off_unallocated_amount",
                "Account-custom_commission_account",
                "Journal Entry Account-custom_is_commission_account",
                "Journal Entry Account-custom_commission_customer",
                "Journal Entry Account-custom_commission_sales_invoice"
            ]]
        ]
    }
]