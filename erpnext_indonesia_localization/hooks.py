app_name = "erpnext_indonesia_localization"
app_title = "Erpnext Indonesia Localization"
app_publisher = "Agile Technica"
app_description = "Localization of ERPNext for Indonesia region, including Indonesia Tax and Charges feature"
app_email = "info@agiletechnica.com"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "erpnext_indonesia_localization",
# 		"logo": "/assets/erpnext_indonesia_localization/logo.png",
# 		"title": "Erpnext Indonesia Localization",
# 		"route": "/erpnext_indonesia_localization",
# 		"has_permission": "erpnext_indonesia_localization.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_indonesia_localization/css/erpnext_indonesia_localization.css"
# app_include_js = "/assets/erpnext_indonesia_localization/js/erpnext_indonesia_localization.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_indonesia_localization/css/erpnext_indonesia_localization.css"
# web_include_js = "/assets/erpnext_indonesia_localization/js/erpnext_indonesia_localization.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_indonesia_localization/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

doctype_js = {
	"Sales Invoice": "public/js/sales_invoice.js",
	"Customer Group": "public/js/customer_group.js",
	"Customer": "public/js/customer.js",
	"Item": "public/js/item.js"
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "erpnext_indonesia_localization/public/icons.svg"

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
# 	"methods": "erpnext_indonesia_localization.utils.jinja_methods",
# 	"filters": "erpnext_indonesia_localization.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_indonesia_localization.install.before_install"
# after_install = "erpnext_indonesia_localization.install.after_install"
after_install = "erpnext_indonesia_localization.utils.install.init_setup_eil"

# Uninstallation
# ------------

# before_uninstall = "erpnext_indonesia_localization.uninstall.before_uninstall"
# after_uninstall = "erpnext_indonesia_localization.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "erpnext_indonesia_localization.utils.before_app_install"
# after_app_install = "erpnext_indonesia_localization.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "erpnext_indonesia_localization.utils.before_app_uninstall"
# after_app_uninstall = "erpnext_indonesia_localization.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_indonesia_localization.notifications.get_notification_config"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"Sales Invoice": {
		"before_cancel": [
			"erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice.set_tin_status_before_cancel_si",
			"erpnext_indonesia_localization.erpnext_indonesia_localization.doc_events.sales_invoice.set_si_had_tin_before"
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_indonesia_localization.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_indonesia_localization.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_indonesia_localization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_indonesia_localization.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_indonesia_localization.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpnext_indonesia_localization.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_indonesia_localization.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_indonesia_localization.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["erpnext_indonesia_localization.utils.before_request"]
# after_request = ["erpnext_indonesia_localization.utils.after_request"]

# Job Events
# ----------
# before_job = ["erpnext_indonesia_localization.utils.before_job"]
# after_job = ["erpnext_indonesia_localization.utils.after_job"]

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
# 	"erpnext_indonesia_localization.auth.validate"
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
					"Sales Invoice-linking_sales_invoice_to_tax_invoice_number",
					"Customer-custom_nik",
					"Country-custom_coretax_countryref",
					"Customer-custom_country",
					"Customer-custom_buyeridtku",
					"Customer-custom_passport_number",
					"Customer-custom_customer_country_code",
					"Customer-custom_customer_email_per_tax_id",
					"UOM Conversion Detail-custom_tax_uom_conversion_rate",
					"UOM Conversion Detail-custom_tax_uom_description",
					"UOM Conversion Detail-custom_tax_uom_code"
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
	},
	{
		"dt": "Role",
		"filters": [
			[
				"name", "in",
				[
					"Pajak Admin",
					"Pajak User"
				]
			]
		]
	},
	{
		"dt": "Indonesia Localization Settings"
	}
]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
