from datetime import date

import frappe
from dateutil.relativedelta import relativedelta

from simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription import (
	Frequency,
	get_calendar_period,
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
		start_date, _ = get_calendar_period(date.today() - relativedelta(months=1), frequency)
		frappe.db.set_value(
			"Simple Subscription",
			subscription_name,
			"start_date",
			start_date,
		)
