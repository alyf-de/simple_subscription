from datetime import date
from dateutil.relativedelta import relativedelta

import frappe
from simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription import (
	get_first_day_of_period,
	Frequency,
)


def execute():
	frappe.reload_doctype("Simple Subscription")

	for subscription_name, frequency in frappe.get_all(
		"Simple Subscription",
		filters={"start_date": ("is", "not set")},
		fields=["name", "frequency"],
		as_list=True,
	):
		frequency = Frequency[frequency]
		frappe.db.set_value(
			"Simple Subscription",
			subscription_name,
			"start_date",
			get_first_day_of_period(date.today() - relativedelta(months=1), frequency),
		)
