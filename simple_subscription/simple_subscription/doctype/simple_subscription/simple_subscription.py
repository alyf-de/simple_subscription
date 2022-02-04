# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from datetime import date, timedelta

import frappe
from frappe.model.document import Document


class SimpleSubscription(Document):
	def create_invoice(self, from_date, to_date):
		invoice = frappe.new_doc("Sales Invoice")
		invoice.customer = self.customer
		for row in self.items:
			invoice.append("items", {
				"item_code": row.item,
				"quantity": row.qty,
			})
		invoice.taxes_and_charges = self.taxes_and_charges
		invoice.from_date = from_date
		invoice.to_date = to_date
		invoice.simple_subscription = self.name
		invoice.set_missing_values()
		invoice.insert()


@frappe.whitelist()
def create_invoice_for_last_month(subscription_name):
	last_day_of_previous_month = date.today().replace(day=1) - timedelta(days=1)
	first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

	subscription = frappe.get_doc("Simple Subscription", subscription_name)
	subscription.create_invoice(first_day_of_previous_month, last_day_of_previous_month)


def process_subscriptions():
	for subscription_name in frappe.get_all(
		"Simple Subscription", filters={"docstatus": 1}, pluck="name"
	):
		create_invoice_for_last_month(subscription_name)
