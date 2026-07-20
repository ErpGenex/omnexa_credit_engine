app_name = "omnexa_credit_engine"
app_title = "ErpGenEx — Credit Engine"
app_publisher = "ErpGenEx"
app_description = "Shared credit engine services"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core"]

add_to_apps_screen = [
	{
		"name": "omnexa_credit_engine",
		"logo": "/assets/omnexa_credit_engine/logo.png",
		"title": "CreditPulse",
		"route": "/app/ce-servicing-portal",
		"has_permission": "omnexa_core.omnexa_core.finance_demo.finance_app_permission.has_app_permission"
	}
]


# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_credit_engine/css/omnexa_credit_engine.css"
# app_include_js = "/assets/omnexa_credit_engine/js/omnexa_credit_engine.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_credit_engine/css/omnexa_credit_engine.css"
# web_include_js = "/assets/omnexa_credit_engine/js/omnexa_credit_engine.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_credit_engine/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_credit_engine/public/icons.svg"

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
# 	"methods": "omnexa_credit_engine.utils.jinja_methods",
# 	"filters": "omnexa_credit_engine.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "omnexa_credit_engine.install.before_install"
# after_install = "omnexa_credit_engine.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "omnexa_credit_engine.uninstall.before_uninstall"
# after_uninstall = "omnexa_credit_engine.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_credit_engine.utils.before_app_install"
# after_app_install = "omnexa_credit_engine.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_credit_engine.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_credit_engine.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_credit_engine.notifications.get_notification_config"

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"omnexa_credit_engine.tasks.all"
# 	],
# 	"daily": [
# 		"omnexa_credit_engine.tasks.daily"
# 	],
# 	"hourly": [
# 		"omnexa_credit_engine.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omnexa_credit_engine.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omnexa_credit_engine.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "omnexa_credit_engine.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_credit_engine.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_credit_engine.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["omnexa_credit_engine.license_gate.before_request"]
# after_request = ["omnexa_credit_engine.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_credit_engine.utils.before_job"]
# after_job = ["omnexa_credit_engine.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"redact_fields": ["{}", "{}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_credit_engine.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


after_migrate = [
	"omnexa_credit_engine.governance_setup.after_migrate",
	"omnexa_credit_engine.workspace_enhancer.after_migrate",
]

permission_query_conditions = {
	"Credit Policy Version": "omnexa_credit_engine.governance_permissions.policy_query_conditions",
	"Credit Audit Snapshot": "omnexa_credit_engine.governance_permissions.snapshot_query_conditions"
	}

has_permission = {
	"Credit Policy Version": "omnexa_credit_engine.governance_permissions.policy_has_permission",
	"Credit Audit Snapshot": "omnexa_credit_engine.governance_permissions.snapshot_has_permission"
	}
