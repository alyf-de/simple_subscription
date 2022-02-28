# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple

import frappe
from frappe import _
from frappe.model.document import Document

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


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
def create_invoice_for_last_period(subscription_name: str) -> SalesInvoice:
	subscription = frappe.get_doc("Simple Subscription", subscription_name)
	invoice_date = get_invoice_date(date.today(), subscription.frequency)
	from_date, to_date = get_period(invoice_date, subscription.frequency)
	return subscription.create_invoice(from_date, to_date)


def process_subscriptions(frequency: str) -> None:
	invoice_date = get_invoice_date(date.today(), frequency)
	from_date, to_date = get_period(invoice_date, frequency)
	for subscription_name in frappe.get_all(
		"Simple Subscription",
		filters={"docstatus": 1, "frequency": frequency, "disabled": ("!=", 1)},
		pluck="name",
	):
		subscription = frappe.get_doc("Simple Subscription", subscription_name)
		try:
			subscription.create_invoice(from_date, to_date)
		except frappe.ValidationError:
			frappe.log_error(frappe.get_traceback())
			continue


def get_period(invoice_date: date, frequency: str) -> Tuple[date, date]:
	frequency_map = {
		"Monthly": 1,
		"Quarterly": 3,
		"Halfyearly": 6,
		"Yearly": 12,
	}

	first_day_of_month = invoice_date.replace(day=1)
	last_day_of_period = first_day_of_month - timedelta(days=1)
	first_day_of_period = first_day_of_month - relativedelta(
		months=frequency_map[frequency]
	)

	return first_day_of_period, last_day_of_period


def get_invoice_date(from_date: date, frequency: str) -> date:
	"""
	Quarterly:
	02.10.2021 -> 01.10.2021
	05.01.2022 -> 01.01.2022
	"""
	invoice_month_map = {
		"Monthly": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
		"Quarterly": [1, 1, 1, 4, 4, 4, 7, 7, 7, 10, 10, 10],
		"Halfyearly": [1] * 6 + [7] * 6,
		"Yearly": [1] * 12,
	}

	first_day_of_month = from_date.replace(day=1)
	invoice_month = invoice_month_map[frequency][first_day_of_month.month - 1]
	months_delta = first_day_of_month.month - invoice_month
	return first_day_of_month - relativedelta(months=months_delta)
