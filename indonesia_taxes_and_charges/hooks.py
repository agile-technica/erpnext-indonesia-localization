from . import __version__ as app_version

app_name = "indonesia_taxes_and_charges"
app_title = "Indonesia Taxes and Charges"
app_publisher = "Agile Technica"
app_description = "Indonesia Taxes and Charges"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@agiletechnica.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/indonesia_taxes_and_charges/css/indonesia_taxes_and_charges.css"
# app_include_js = "/assets/indonesia_taxes_and_charges/js/indonesia_taxes_and_charges.js"

# include js, css files in header of web template
# web_include_css = "/assets/indonesia_taxes_and_charges/css/indonesia_taxes_and_charges.css"
# web_include_js = "/assets/indonesia_taxes_and_charges/js/indonesia_taxes_and_charges.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "indonesia_taxes_and_charges/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
doctype_js = {
	"Sales Invoice": "public/js/sales_invoice.js",
	"Customer Group": "public/js/customer_group.js"
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "indonesia_taxes_and_charges.install.before_install"
# after_install = "indonesia_taxes_and_charges.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "indonesia_taxes_and_charges.uninstall.before_uninstall"
# after_uninstall = "indonesia_taxes_and_charges.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "indonesia_taxes_and_charges.notifications.get_notification_config"

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
	"Sales Invoice": {
		"before_cancel": [
			"indonesia_taxes_and_charges.indonesia_taxes_and_charges.doc_events.sales_invoice.set_tin_status_before_cancel_si",
			"indonesia_taxes_and_charges.indonesia_taxes_and_charges.doc_events.sales_invoice.set_si_had_tin_before"
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"indonesia_taxes_and_charges.tasks.all"
# 	],
# 	"daily": [
# 		"indonesia_taxes_and_charges.tasks.daily"
# 	],
# 	"hourly": [
# 		"indonesia_taxes_and_charges.tasks.hourly"
# 	],
# 	"weekly": [
# 		"indonesia_taxes_and_charges.tasks.weekly"
# 	]
# 	"monthly": [
# 		"indonesia_taxes_and_charges.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "indonesia_taxes_and_charges.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "indonesia_taxes_and_charges.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "indonesia_taxes_and_charges.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


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
# 	"indonesia_taxes_and_charges.auth.validate"
# ]
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"name", "in",
				[
					"Customer Group-customer_tax_code",
					"Customer Group-kode_pajak",
					"Sales Invoice-custom_tax_invoice_number",
					"Customer-company_address_tax_id",
					"Customer-company_name_tax_id",
					"Customer-customer_pkp",
					"Sales Invoice-custom_si_had_tin_before",
					"Sales Invoice-tax_additional_description",
					"Sales Invoice-tax_additional_reference",
					"Sales Invoice-linking_sales_invoice_to_tax_invoice_number"

				]
			]
		]
	},
	{
		"dt": "Property Setter",
		"filters": [
			[
				"name", "in",
				[
					"Sales Invoice-tax_id-fetch_from"
				]
			]
		]
	}
]
# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
