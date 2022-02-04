import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def after_install():
	make_property_setter("Sales Invoice", "from_date", "allow_on_submit", 0, "Check")
	make_property_setter("Sales Invoice", "to_date", "allow_on_submit", 0, "Check")
	create_custom_field(
		"Sales Invoice",
		dict(
			fieldname="simple_subscription",
			label="Simple Subscription",
			fieldtype="Link",
			insert_after="to_date",
			options="Simple Subscription",
			read_only=1,
		),
	)
	copy_subscriptions()


def copy_subscriptions():
	"""Create Simple Subscriptions from existing ERPNext Subscriptions"""
	for subscription_name in frappe.get_all(
		"Subscription",
		{"status": ("!=", "Cancelled"), "party_type": "Customer"},
		pluck="name",
	):
		subscription = frappe.get_doc("Subscription", subscription_name)
		create_simple_subscription(
			customer=subscription.party,
			items=[
				{
					"item": frappe.db.get_value(
						"Subscription Plan", row.plan, "item"
					),
					"qty": row.qty,
				}
				for row in subscription.plans
			],
			taxes_and_charges=subscription.sales_tax_template,
		)


def create_simple_subscription(customer, items, taxes_and_charges):
	simple_subscription = frappe.new_doc("Simple Subscription")
	simple_subscription.customer = customer
	simple_subscription.extend("items", items)
	simple_subscription.taxes_and_charges = taxes_and_charges
	simple_subscription.insert()
