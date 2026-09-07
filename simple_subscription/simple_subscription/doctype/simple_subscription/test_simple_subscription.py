# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

import unittest
from datetime import date

import frappe

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


class TestSubscriptionCustomerData(unittest.TestCase):
	"""Address/Contact prefill: customer-bound validation and forwarding to the invoice.

	Deliberately a plain TestCase: frappe.tests.IntegrationTestCase would resolve the test
	record dependencies of Simple Subscription, which pulls in ERPNext's whole object graph
	(including every Company test record) and breaks on a fresh site. Everything needed here
	is created below instead.
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.currency = frappe.defaults.get_global_default("currency")
		cls.company = make_company(cls.currency)
		cls.item = make_item()
		cls.customer = make_customer("_Test Sub Customer")
		cls.other_customer = make_customer("_Test Sub Other Customer")
		cls.address = make_address("_Test Sub Billing", cls.customer, "Rechnungsweg 1", primary=True)
		cls.shipping_address = make_address("_Test Sub Shipping", cls.customer, "Lieferweg 2", shipping=True)
		cls.other_address = make_address("_Test Sub Foreign", cls.other_customer, "Fremdweg 3")
		cls.contact = make_contact("_Test Sub Contact", cls.customer)
		cls.other_contact = make_contact("_Test Sub Foreign Contact", cls.other_customer)
		frappe.db.commit()

	def tearDown(self):
		frappe.db.rollback()

	def make_subscription(self, **kwargs):
		return frappe.get_doc(
			doctype="Simple Subscription",
			company=self.company,
			customer=self.customer,
			currency=self.currency,
			start_date="2024-01-01",
			frequency="Yearly",
			items=[{"item": self.item, "qty": 1}],
			**kwargs,
		)

	def test_rejects_links_of_another_customer(self):
		for fieldname, value in (
			("customer_address", self.other_address),
			("shipping_address_name", self.other_address),
			("contact_person", self.other_contact),
		):
			with self.subTest(fieldname=fieldname):
				subscription = self.make_subscription(**{fieldname: value})
				self.assertRaises(frappe.ValidationError, subscription.insert)

	def test_rejects_links_still_stale_after_submit(self):
		"""The links are allow_on_submit, so validate() no longer guards them."""
		subscription = self.make_subscription(customer_address=self.address).insert()
		subscription.submit()

		subscription.customer_address = self.other_address
		# must be the ownership check, not the generic "cannot change after submit" guard
		self.assertRaisesRegex(frappe.ValidationError, "does not belong to Customer", subscription.save)

	def test_virtual_fields_render_linked_records(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.shipping_address,
			contact_person=self.contact,
		).insert()

		self.assertIn("Rechnungsweg 1", subscription.billing_address_display)
		self.assertIn("Lieferweg 2", subscription.shipping_address_display)
		self.assertEqual(subscription.contact_display, "_Test Sub Contact")

	def test_virtual_fields_are_empty_without_links(self):
		subscription = self.make_subscription().insert()

		self.assertIsNone(subscription.billing_address_display)
		self.assertIsNone(subscription.shipping_address_display)
		self.assertIsNone(subscription.contact_display)

	def test_forwards_links_to_invoice(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.shipping_address,
			contact_person=self.contact,
		).insert()
		subscription.submit()

		invoice = subscription.create_invoice(date(2024, 1, 1), date(2024, 12, 31))

		self.assertEqual(invoice.customer_address, self.address)
		self.assertEqual(invoice.shipping_address_name, self.shipping_address)
		self.assertEqual(invoice.contact_person, self.contact)
		# the whole contact block must come from the chosen contact, not the customer default
		self.assertEqual(invoice.contact_display, "_Test Sub Contact")

	def test_invoice_falls_back_to_customer_defaults(self):
		subscription = self.make_subscription().insert()
		subscription.submit()

		invoice = subscription.create_invoice(date(2024, 1, 1), date(2024, 12, 31))

		self.assertEqual(invoice.customer_address, self.address)
		self.assertEqual(invoice.shipping_address_name, self.shipping_address)


def make_company(currency: str) -> str:
	"""A company in the site's own currency, so the invoice does not trip the party-account check."""
	name = "_Test Sub Company"
	if not frappe.db.exists("Company", name):
		frappe.get_doc(
			doctype="Company",
			company_name=name,
			abbr="_TSC",
			default_currency=currency,
			country="Germany",
		).insert()
	return name


def make_item() -> str:
	name = "_Test Sub Item"
	if not frappe.db.exists("Item", name):
		frappe.get_doc(
			doctype="Item",
			item_code=name,
			item_group="All Item Groups",
			stock_uom="Nos",
			is_stock_item=0,
			is_sales_item=1,
		).insert()
	return name


def make_customer(name: str) -> str:
	if not frappe.db.exists("Customer", name):
		frappe.get_doc(doctype="Customer", customer_name=name).insert()
	return name


def make_address(title: str, customer: str, line1: str, primary=False, shipping=False) -> str:
	name = f"{title}-Billing"
	if not frappe.db.exists("Address", name):
		frappe.get_doc(
			doctype="Address",
			address_title=title,
			address_type="Billing",
			address_line1=line1,
			city="Berlin",
			country="Germany",
			is_primary_address=int(primary),
			is_shipping_address=int(shipping),
			links=[{"link_doctype": "Customer", "link_name": customer}],
		).insert()
	return name


def make_contact(first_name: str, customer: str) -> str:
	name = f"{first_name}-{customer}"
	if not frappe.db.exists("Contact", name):
		frappe.get_doc(
			doctype="Contact",
			first_name=first_name,
			links=[{"link_doctype": "Customer", "link_name": customer}],
		).insert()
	return name
