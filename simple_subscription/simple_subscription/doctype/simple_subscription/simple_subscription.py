# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

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
def create_invoice_for_last_period(subscription_name):
	subscription = frappe.get_doc("Simple Subscription", subscription_name)
	from_date, to_date = get_dates(subscription.frequency)
	subscription.create_invoice(from_date, to_date)


def process_subscriptions(frequency):
	from_date, to_date = get_dates(frequency)
	for subscription_name in frappe.get_all(
		"Simple Subscription",
		filters={"docstatus": 1, "frequency": frequency},
		pluck="name",
	):
		subscription = frappe.get_doc("Simple Subscription", subscription_name)
		subscription.create_invoice(from_date, to_date)


def get_dates(frequency: str):
	months = {
		"Monthly": 1,
		"Quarterly": 3,
		"Halfyearly": 6,
		"Yearly": 12,
	}
	first_day_of_month = date.today().replace(day=1)
	last_day_of_period = first_day_of_month - timedelta(days=1)
	first_day_of_period = first_day_of_month - relativedelta(months=months[frequency])

	return first_day_of_period, last_day_of_period
