from . import __version__ as app_version

app_name = "simple_subscription"
app_title = "Simple Subscription"
app_publisher = "ALYF GmbH"
app_description = "Simple monthly subscription"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "hallo@alyf.de"
app_license = "MIT"
required_apps = ["erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/simple_subscription/css/simple_subscription.css"
# app_include_js = "/assets/simple_subscription/js/simple_subscription.js"

# include js, css files in header of web template
# web_include_css = "/assets/simple_subscription/css/simple_subscription.css"
# web_include_js = "/assets/simple_subscription/js/simple_subscription.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "simple_subscription/public/scss/website"

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

# before_install = "simple_subscription.install.before_install"
after_install = "simple_subscription.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "simple_subscription.uninstall.before_uninstall"
# after_uninstall = "simple_subscription.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "simple_subscription.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		# m h dom m dow
		"0 0 1 * *": [	# At 12:00 AM, on day 1 of the month
			"simple_subscription.tasks.monthly"
		],
		"0 0 1 1,4,7,10 *": [  # At 12:00 AM, on day 1 of the month, only in January, April, July, and October
			"simple_subscription.tasks.quarterly"
		],
		"0 0 1 1,7 *": [  # At 12:00 AM, on day 1 of the month, only in January and July
			"simple_subscription.tasks.halfyearly"
		],
		"0 0 1 1 *": [	# At 12:00 AM, on day 1 of the month, only in January
			"simple_subscription.tasks.yearly"
		],
	},
}

# 01.04.

# Testing
# -------

# before_tests = "simple_subscription.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "simple_subscription.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "simple_subscription.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{"doctype": "{doctype_4}"},
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"simple_subscription.auth.validate"
# ]
