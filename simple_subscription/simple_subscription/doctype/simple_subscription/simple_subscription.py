# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Union, Tuple
from enum import Enum

import frappe
from frappe import _
from frappe.model.document import Document

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class Frequency(Enum):
	Monthly = 1
	Quarterly = 3
	Halfyearly = 6
	Yearly = 12


class PeriodType(Enum):
	CalendarMonths = "calendar months"
	StartDate = "start date"


class BillingTime(Enum):
	AtBeginningOfPeriod = "at beginning of period"
	AfterEndOfPeriod = "after end of period"


class SimpleSubscription(Document):
	def create_invoice(self, from_date: date, to_date: date) -> SalesInvoice:
		msg = None
		if self.disabled:
			msg = _("Please enable Subscription {0} before creating a Sales Invoice.")

		if self.docstatus == 0:
			msg = _("Please submit Subscription {0} before creating a Sales Invoice.")

		if self.docstatus == 2:
			msg = _("Please amend Subscription {0} before creating a Sales Invoice.")

		if msg:
			frappe.throw(msg.format(self.name))

		invoice = frappe.new_doc("Sales Invoice")
		invoice.company = self.company
		invoice.customer = self.customer
		for row in self.items:
			invoice.append(
				"items",
				{
					"item_code": row.item,
					"qty": row.qty,
				},
			)
		invoice.taxes_and_charges = self.taxes_and_charges
		invoice.from_date = from_date
		invoice.to_date = to_date
		invoice.simple_subscription = self.name
		invoice.set_missing_values()
		return invoice.insert()


@frappe.whitelist()
def create_current_invoice(subscription_name: str, silent=False):
	subscription = frappe.get_doc("Simple Subscription", subscription_name)
	from_date, to_date = get_from_and_to_date(
		frequency=Frequency[subscription.frequency],
		eval_date=date.today(),
		period_type=PeriodType(subscription.period_type),
		billing_time=BillingTime(subscription.billing_time),
		start_date=subscription.start_date,
	)

	# check that start_date is not in the future
	if subscription.start_date and subscription.start_date > from_date:
		if not silent:
			frappe.throw(
				_(
					f"Subscription starts after the first day of the current period ({from_date})."
				)
			)
		return

	existing_si = get_existing_sales_invoice(subscription_name, from_date, to_date)
	if existing_si:
		if not silent:
			frappe.throw(
				_("Sales Invoice already exists for this period: {}").format(
					existing_si
				)
			)
		return

	subscription.create_invoice(from_date, to_date)


def process_simple_subscriptions() -> None:
	for subscription_name in get_active_subscriptions():
		try:
			create_current_invoice(subscription_name, silent=True)
		except frappe.ValidationError:
			frappe.log_error(frappe.get_traceback())
			continue


def get_existing_sales_invoice(
	subscription_name: str, from_date: date, to_date: date
) -> Union[str, None]:
	return frappe.db.exists(
		{
			"doctype": "Sales Invoice",
			"simple_subscription": subscription_name,
			"from_date": from_date,
			"to_date": to_date,
		}
	)


def get_active_subscriptions():
	return frappe.get_all(
		"Simple Subscription",
		filters={
			"docstatus": 1,
			"disabled": ("!=", 1),
			"start_date": ("<=", date.today()),
		},
		pluck="name",
	)


def get_from_and_to_date(
	frequency: Frequency,
	eval_date: date,
	period_type: PeriodType | None = None,
	billing_time: BillingTime | None = None,
	start_date: date | None = None,
) -> Tuple[date, date]:
	"""Return the first day and last day of the period.

	:param frequency: Frequency of the subscription
	:param eval_date: Date to evaluate the period for
	:param period_type: Type of period to evaluate, defaults to CalendarMonths
	:param billing_time: Time to bill the subscription, defaults to AfterEndOfPeriod
	:param start_date: Start date of the subscription, required only for PeriodType.StartDate
	"""
	if period_type == PeriodType.StartDate and not start_date:
		raise ValueError("start_date is required for period_type 'start date'")

	if not period_type:
		period_type = PeriodType.CalendarMonths

	if not billing_time:
		billing_time = BillingTime.AfterEndOfPeriod

	if (
		period_type == PeriodType.StartDate
		and billing_time == BillingTime.AtBeginningOfPeriod
	):
		return get_date_period(eval_date, frequency, start_date)
	elif (
		period_type == PeriodType.StartDate
		and billing_time == BillingTime.AfterEndOfPeriod
	):
		current_period_start, current_period_end = get_date_period(
			eval_date, frequency, start_date
		)
		return get_date_period(
			current_period_start - timedelta(days=1),
			frequency,
			start_date,
		)
	elif (
		period_type == PeriodType.CalendarMonths
		and billing_time == BillingTime.AtBeginningOfPeriod
	):
		return get_calendar_period(eval_date, frequency)
	elif (
		period_type == PeriodType.CalendarMonths
		and billing_time == BillingTime.AfterEndOfPeriod
	):
		current_period_start, current_period_end = get_calendar_period(
			eval_date, frequency
		)
		return get_calendar_period(current_period_start - timedelta(days=1), frequency)


def get_calendar_period(eval_date: date, frequency: Frequency) -> Tuple[date, date]:
	"""Return the first day and last day of the period containing `from_date`."""
	invoice_month_map = {
		Frequency.Monthly: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
		Frequency.Quarterly: [1, 1, 1, 4, 4, 4, 7, 7, 7, 10, 10, 10],
		Frequency.Halfyearly: [1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7],
		Frequency.Yearly: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
	}
	no_of_month_map = {
		Frequency.Monthly: 1,
		Frequency.Quarterly: 3,
		Frequency.Halfyearly: 6,
		Frequency.Yearly: 12,
	}

	from_date = eval_date.replace(
		day=1, month=invoice_month_map[frequency][eval_date.month - 1]
	)
	to_date = (
		from_date
		+ relativedelta(months=no_of_month_map[frequency])
		- relativedelta(days=1)
	)

	return from_date, to_date


def get_date_period(
	eval_date: date, frequency: Frequency, initial_date: date
) -> Tuple[date, date]:
	no_of_month_map = {
		Frequency.Monthly: 1,
		Frequency.Quarterly: 3,
		Frequency.Halfyearly: 6,
		Frequency.Yearly: 12,
	}

	delta = relativedelta(eval_date, initial_date)

	# determine no of period eval_date lies in when starting on initial_date
	if eval_date >= initial_date:
		month_detla_floor = (delta.years * 12 + delta.months) // no_of_month_map[
			frequency
		]
	else:
		month_detla_floor = (delta.years * 12 + delta.months - 1) // no_of_month_map[
			frequency
		]

	from_date = initial_date + relativedelta(
		months=(no_of_month_map[frequency] * month_detla_floor)
	)
	to_date = (
		from_date
		+ relativedelta(months=no_of_month_map[frequency])
		- relativedelta(days=1)
	)

	return from_date, to_date
