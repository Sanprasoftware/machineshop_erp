app_name = "quantbit_machineshop_erp"
app_title = "Quantbit MachineShop ERP"
app_publisher = "Quantbit Technlogies Pvt Ltd"
app_description = "Our cutting-edge Quantbit_MachineShop_ERP is designed to revolutionize the way machine shops manage their operations. Tailored specifically for the unique needs of the machine shop industry, this comprehensive ERP solution integrates all aspects of machine shop management into a single, user-friendly platform."
app_email = "support@quantbit.io"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------ vivek kumbhargkjgjgjg
# include js, css files in header of desk.html
# app_include_css = "/assets/quantbit_machineshop_erp/css/quantbit_machineshop_erp.css"
# app_include_js = "/assets/quantbit_machineshop_erp/js/quantbit_machineshop_erp.js"
app_include_js = "/assets/quantbit_machineshop_erp/js/custom_navbar.js"
# include js, css files in header of web template
# web_include_css = "/assets/quantbit_machineshop_erp/css/quantbit_machineshop_erp.css"
# web_include_js = "/assets/quantbit_machineshop_erp/js/quantbit_machineshop_erp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "quantbit_machineshop_erp/public/scss/website"

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
# app_include_icons = "quantbit_machineshop_erp/public/icons.svg"

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
# 	"methods": "quantbit_machineshop_erp.utils.jinja_methods",
# 	"filters": "quantbit_machineshop_erp.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "quantbit_machineshop_erp.install.before_install"
# after_install = "quantbit_machineshop_erp.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "quantbit_machineshop_erp.uninstall.before_uninstall"
# after_uninstall = "quantbit_machineshop_erp.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "quantbit_machineshop_erp.utils.before_app_install"
# after_app_install = "quantbit_machineshop_erp.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "quantbit_machineshop_erp.utils.before_app_uninstall"
# after_app_uninstall = "quantbit_machineshop_erp.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "quantbit_machineshop_erp.notifications.get_notification_config"

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
# 		"quantbit_machineshop_erp.tasks.all"
# 	],
# 	"daily": [
# 		"quantbit_machineshop_erp.tasks.daily"
# 	],
# 	"hourly": [
# 		"quantbit_machineshop_erp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"quantbit_machineshop_erp.tasks.weekly"
# 	],
# 	"monthly": [
# 		"quantbit_machineshop_erp.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "quantbit_machineshop_erp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "quantbit_machineshop_erp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "quantbit_machineshop_erp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["quantbit_machineshop_erp.utils.before_request"]
# after_request = ["quantbit_machineshop_erp.utils.after_request"]

# Job Events
# ----------
# before_job = ["quantbit_machineshop_erp.utils.before_job"]
# after_job = ["quantbit_machineshop_erp.utils.after_job"]

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
# 	"quantbit_machineshop_erp.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

doctype_js = {
    "MachineShop Filter Setting": "public/js/filter.js",
    "MachineShop Operator Master":"public/js/filter.js",
    "Item":"public/js/filter.js"
}

fixtures = [
   
    {
        "doctype": "Stock Entry Type",
        "filters": [
            ["name", "in", ["Machining Manufacturing","Machining Rejection","Downstream Manufacturing","Downstream Material Transfer","Machining In Process Manufacturing","Downstream In Process Manufacturing"]]
        ],
    },
    {
        "doctype": "Inventory Dimension",
        "filters": [
            ["name", "in", ["MachineShop Operation"]]
        ],
    }
]

