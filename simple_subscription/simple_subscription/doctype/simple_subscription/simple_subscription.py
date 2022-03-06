# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Union
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
def create_invoice_for_previous_period(subscription_name: str, silent=False):
	subscription = frappe.get_doc("Simple Subscription", subscription_name)
	frequency = Frequency[subscription.frequency]
	reference_date = get_first_day_of_period(date.today(), frequency)
	to_date = reference_date - timedelta(days=1)
	from_date = get_first_day_of_period(to_date, frequency)

	if subscription.start_date > from_date:
		if not silent:
			frappe.throw(
				_("Subscription started after the first day of the last period.")
			)
		return

	existing_si = get_existing_sales_invoice(subscription.name, from_date, to_date)
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
			create_invoice_for_previous_period(subscription_name, silent=True)
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
			"start_date": from_date,
			"end_date": to_date,
		}
	)


def get_active_subscriptions():
	return frappe.get_all(
		"Simple Subscription",
		filters={"docstatus": 1, "disabled": ("!=", 1)},
		pluck="name",
	)


def get_first_day_of_period(from_date: date, frequency: Frequency) -> date:
	"""Return the first day of the period containing `from_date`."""
	invoice_month_map = {
		Frequency.Monthly: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
		Frequency.Quarterly: [1, 1, 1, 4, 4, 4, 7, 7, 7, 10, 10, 10],
		Frequency.Halfyearly: [1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7],
		Frequency.Yearly: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
	}

	first_day_of_month = from_date.replace(day=1)
	invoice_month = invoice_month_map[frequency][first_day_of_month.month - 1]
	months_delta = first_day_of_month.month - invoice_month

	return first_day_of_month - relativedelta(months=months_delta)
