# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

import unittest
from datetime import date

import frappe
from frappe.tests import IntegrationTestCase

from .simple_subscription import (
	BillingTime,
	Frequency,
	PeriodType,
	get_calendar_period,
	get_date_period,
	get_from_and_to_date,
	validate_calendar_frequencies,
)


class TestSimpleSubscription(unittest.TestCase):
	def test_get_calendar_period(self):
		eval_date = date(2022, 11, 7)

		from_date, to_date = get_calendar_period(eval_date, Frequency.Monthly)
		self.assertEqual(from_date, date(2022, 11, 1))
		self.assertEqual(to_date, date(2022, 11, 30))

		from_date, to_date = get_calendar_period(eval_date, Frequency.Quarterly)
		self.assertEqual(from_date, date(2022, 10, 1))
		self.assertEqual(to_date, date(2022, 12, 31))

		from_date, to_date = get_calendar_period(eval_date, Frequency.Halfyearly)
		self.assertEqual(from_date, date(2022, 7, 1))
		self.assertEqual(to_date, date(2022, 12, 31))

		from_date, to_date = get_calendar_period(eval_date, Frequency.Yearly)
		self.assertEqual(from_date, date(2022, 1, 1))
		self.assertEqual(to_date, date(2022, 12, 31))

		start_year = date(2022, 6, 25).year

		from_date, to_date = get_calendar_period(date(2022, 11, 7), Frequency.Biennial, start_year)
		self.assertEqual(from_date, date(2022, 1, 1))
		self.assertEqual(to_date, date(2023, 12, 31))

		from_date, to_date = get_calendar_period(date(2023, 6, 15), Frequency.Biennial, start_year)
		self.assertEqual(from_date, date(2022, 1, 1))
		self.assertEqual(to_date, date(2023, 12, 31))

		from_date, to_date = get_calendar_period(date(2024, 3, 1), Frequency.Biennial, start_year)
		self.assertEqual(from_date, date(2024, 1, 1))
		self.assertEqual(to_date, date(2025, 12, 31))

		from_date, to_date = get_calendar_period(date(2024, 6, 15), Frequency.Triennial, start_year)
		self.assertEqual(from_date, date(2022, 1, 1))
		self.assertEqual(to_date, date(2024, 12, 31))

		from_date, to_date = get_calendar_period(date(2025, 1, 1), Frequency.Triennial, start_year)
		self.assertEqual(from_date, date(2025, 1, 1))
		self.assertEqual(to_date, date(2027, 12, 31))

	def test_get_calendar_period_multi_year_requires_start_year(self):
		with self.assertRaises(ValueError):
			get_calendar_period(date(2022, 11, 7), Frequency.Biennial)

		with self.assertRaises(ValueError):
			get_calendar_period(date(2022, 11, 7), Frequency.Triennial)

	def test_validate_calendar_frequencies(self):
		with self.assertRaises(frappe.ValidationError):
			validate_calendar_frequencies("calendar months", "Biennial", None)

		with self.assertRaises(frappe.ValidationError):
			validate_calendar_frequencies("calendar months", "Triennial", None)

		validate_calendar_frequencies("calendar months", "Biennial", date(2022, 6, 25))
		validate_calendar_frequencies("start date", "Biennial", None)
		validate_calendar_frequencies("calendar months", "Yearly", None)

	def test_get_date_period(self):
		eval_date = date(2022, 11, 7)
		initial_date = date(2022, 6, 25)

		from_date, to_date = get_date_period(eval_date, Frequency.Monthly, initial_date)
		self.assertEqual(from_date, date(2022, 10, 25))
		self.assertEqual(to_date, date(2022, 11, 24))

		from_date, to_date = get_date_period(eval_date, Frequency.Quarterly, initial_date)
		self.assertEqual(from_date, date(2022, 9, 25))
		self.assertEqual(to_date, date(2022, 12, 24))

		from_date, to_date = get_date_period(eval_date, Frequency.Halfyearly, initial_date)
		self.assertEqual(from_date, date(2022, 6, 25))
		self.assertEqual(to_date, date(2022, 12, 24))

		from_date, to_date = get_date_period(eval_date, Frequency.Yearly, initial_date)
		self.assertEqual(from_date, date(2022, 6, 25))
		self.assertEqual(to_date, date(2023, 6, 24))

		from_date, to_date = get_date_period(eval_date, Frequency.Biennial, initial_date)
		self.assertEqual(from_date, date(2022, 6, 25))
		self.assertEqual(to_date, date(2024, 6, 24))

		from_date, to_date = get_date_period(eval_date, Frequency.Triennial, initial_date)
		self.assertEqual(from_date, date(2022, 6, 25))
		self.assertEqual(to_date, date(2025, 6, 24))

	def test_get_from_and_to_date(self):
		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Monthly,
			period_type=PeriodType.CalendarMonths,
			billing_time=BillingTime.AtBeginningOfPeriod,
			eval_date=date(2022, 11, 7),
			start_date=date(2022, 11, 7),
		)
		self.assertEqual(from_date, date(2022, 11, 1))
		self.assertEqual(to_date, date(2022, 11, 30))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Monthly,
			period_type=PeriodType.CalendarMonths,
			billing_time=BillingTime.AfterEndOfPeriod,
			eval_date=date(2022, 11, 7),
			start_date=date(2022, 10, 1),
		)
		self.assertEqual(from_date, date(2022, 10, 1))
		self.assertEqual(to_date, date(2022, 10, 31))

		# previous behavior should be the default
		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Monthly,
			period_type=None,
			billing_time=None,
			eval_date=date(2022, 11, 7),
			start_date=date(2022, 10, 1),
		)
		self.assertEqual(from_date, date(2022, 10, 1))
		self.assertEqual(to_date, date(2022, 10, 31))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Monthly,
			period_type=PeriodType.StartDate,
			billing_time=BillingTime.AtBeginningOfPeriod,
			eval_date=date(2022, 11, 7),
			start_date=date(2022, 11, 5),
		)
		self.assertEqual(from_date, date(2022, 11, 5))
		self.assertEqual(to_date, date(2022, 12, 4))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Monthly,
			period_type=PeriodType.StartDate,
			billing_time=BillingTime.AfterEndOfPeriod,
			eval_date=date(2022, 11, 7),
			start_date=date(2022, 10, 5),
		)
		self.assertEqual(from_date, date(2022, 10, 5))
		self.assertEqual(to_date, date(2022, 11, 4))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Biennial,
			period_type=PeriodType.StartDate,
			billing_time=BillingTime.AtBeginningOfPeriod,
			eval_date=date(2024, 11, 7),
			start_date=date(2022, 6, 25),
		)
		self.assertEqual(from_date, date(2024, 6, 25))
		self.assertEqual(to_date, date(2026, 6, 24))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Triennial,
			period_type=PeriodType.StartDate,
			billing_time=BillingTime.AfterEndOfPeriod,
			eval_date=date(2026, 1, 1),
			start_date=date(2022, 6, 25),
		)
		self.assertEqual(from_date, date(2022, 6, 25))
		self.assertEqual(to_date, date(2025, 6, 24))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Biennial,
			period_type=PeriodType.CalendarMonths,
			billing_time=BillingTime.AtBeginningOfPeriod,
			eval_date=date(2023, 6, 15),
			start_date=date(2022, 6, 25),
		)
		self.assertEqual(from_date, date(2022, 1, 1))
		self.assertEqual(to_date, date(2023, 12, 31))

		from_date, to_date = get_from_and_to_date(
			frequency=Frequency.Biennial,
			period_type=PeriodType.CalendarMonths,
			billing_time=BillingTime.AfterEndOfPeriod,
			eval_date=date(2023, 12, 31),
			start_date=date(2022, 6, 25),
		)
		self.assertEqual(from_date, date(2020, 1, 1))
		self.assertEqual(to_date, date(2021, 12, 31))


class TestSubscriptionCustomerData(IntegrationTestCase):
	"""Address/Contact prefill: customer-bound validation and forwarding to the invoice."""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.customer = frappe.get_doc(doctype="Customer", customer_name="_Test Sub Customer").insert()
		cls.other_customer = frappe.get_doc(
			doctype="Customer", customer_name="_Test Sub Other Customer"
		).insert()
		cls.address = make_address("_Test Sub Billing", cls.customer.name, "Rechnungsweg 1")
		cls.shipping_address = make_address("_Test Sub Shipping", cls.customer.name, "Lieferweg 2")
		cls.other_address = make_address("_Test Sub Foreign", cls.other_customer.name, "Fremdweg 3")
		cls.contact = make_contact("_Test Sub Contact", cls.customer.name)

	def make_subscription(self, **kwargs):
		return frappe.get_doc(
			doctype="Simple Subscription",
			company="_Test Company",
			customer=self.customer.name,
			start_date="2024-01-01",
			frequency="Yearly",
			items=[{"item": "_Test Item", "qty": 1}],
			**kwargs,
		)

	def test_rejects_address_of_another_customer(self):
		subscription = self.make_subscription(customer_address=self.other_address)
		self.assertRaises(frappe.ValidationError, subscription.insert)

	def test_virtual_fields_render_linked_records(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.shipping_address,
			contact_person=self.contact,
		).insert()

		self.assertIn("Rechnungsweg 1", subscription.billing_address_display)
		self.assertIn("Lieferweg 2", subscription.shipping_address_display)
		self.assertEqual(subscription.contact_display, "_Test Sub Contact")

	def test_forwards_links_to_invoice(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.shipping_address,
			contact_person=self.contact,
		).insert()
		subscription.submit()

		invoice = subscription.create_invoice(date(2024, 1, 1), date(2024, 12, 31))

		self.assertIn(invoice.customer_address, (self.address, self.shipping_address))
		self.assertEqual(invoice.shipping_address_name, self.shipping_address)
		self.assertEqual(invoice.contact_person, self.contact)
		self.assertEqual(invoice.contact_display, "_Test Sub Contact")

	def test_invoice_falls_back_to_customer_defaults(self):
		subscription = self.make_subscription().insert()
		subscription.submit()

		invoice = subscription.create_invoice(date(2024, 1, 1), date(2024, 12, 31))

		self.assertIn(invoice.customer_address, (self.address, self.shipping_address))


def make_address(title: str, customer: str, line1: str) -> str:
	return frappe.get_doc(
		doctype="Address",
		address_title=title,
		address_type="Billing",
		address_line1=line1,
		city="Berlin",
		country="Germany",
		links=[{"link_doctype": "Customer", "link_name": customer}],
	).insert().name


def make_contact(first_name: str, customer: str) -> str:
	return frappe.get_doc(
		doctype="Contact",
		first_name=first_name,
		links=[{"link_doctype": "Customer", "link_name": customer}],
	).insert().name
