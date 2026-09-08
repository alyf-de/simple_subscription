# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

import unittest
from datetime import date

import frappe

from .simple_subscription import (
	CUSTOMER_LINK_FIELDS,
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
	"""Customer-bound Address/Contact links: the ownership check and the display properties.

	Kept deliberately light. Generating the invoice needs a fully set-up ERPNext site -- Company,
	Item Group, UOM, Price List, Fiscal Year -- fixtures that only the setup wizard creates and
	that CI (a bare `install-app erpnext`) does not have. So these exercise the app's own logic on
	an in-memory document, plus a meta check that the fieldnames create_invoice() forwards still
	line up with the Sales Invoice.
	"""

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# never committed, so the fixtures die with the transaction -- same as IntegrationTestCase
		cls.addClassCleanup(frappe.db.rollback)
		make_default_address_template()
		cls.customer = make_customer("_Test Sub Customer")
		cls.other_customer = make_customer("_Test Sub Other Customer")
		cls.address = make_address("_Test Sub Billing", cls.customer, "Rechnungsweg 1")
		cls.other_address = make_address("_Test Sub Foreign", cls.other_customer, "Fremdweg 3")
		cls.contact = make_contact("_Test Sub Contact", cls.customer)
		cls.other_contact = make_contact("_Test Sub Foreign Contact", cls.other_customer)

	def make_subscription(self, **kwargs):
		subscription = frappe.new_doc("Simple Subscription")
		subscription.customer = self.customer
		subscription.update(kwargs)
		return subscription

	def test_accepts_links_of_the_same_customer(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.address,
			contact_person=self.contact,
		)
		subscription.validate_customer_links()  # must not raise

	def test_accepts_empty_links(self):
		self.make_subscription().validate_customer_links()  # must not raise

	def test_rejects_links_of_another_customer(self):
		for fieldname, value in (
			("customer_address", self.other_address),
			("shipping_address_name", self.other_address),
			("contact_person", self.other_contact),
		):
			with self.subTest(fieldname=fieldname):
				subscription = self.make_subscription(**{fieldname: value})
				self.assertRaisesRegex(
					frappe.ValidationError,
					"does not belong to Customer",
					subscription.validate_customer_links,
				)

	def test_guards_the_links_after_submit_too(self):
		"""The fields are allow_on_submit, so validate() no longer runs once they change."""
		meta = frappe.get_meta("Simple Subscription")
		for fieldname in CUSTOMER_LINK_FIELDS:
			self.assertTrue(meta.get_field(fieldname).allow_on_submit, fieldname)

		subscription = self.make_subscription(customer_address=self.other_address)
		self.assertRaisesRegex(
			frappe.ValidationError,
			"does not belong to Customer",
			subscription.before_update_after_submit,
		)

	def test_display_properties_render_linked_records(self):
		subscription = self.make_subscription(
			customer_address=self.address,
			shipping_address_name=self.address,
			contact_person=self.contact,
		)

		self.assertIn("Rechnungsweg 1", subscription.billing_address_display)
		self.assertIn("Rechnungsweg 1", subscription.shipping_address_display)
		self.assertEqual(subscription.contact_display, "_Test Sub Contact")

	def test_display_properties_are_empty_without_links(self):
		subscription = self.make_subscription()

		self.assertIsNone(subscription.billing_address_display)
		self.assertIsNone(subscription.shipping_address_display)
		self.assertIsNone(subscription.contact_display)

	def test_link_fields_match_the_sales_invoice(self):
		"""create_invoice() forwards these by name, so both doctypes have to spell them the same.

		The forwarding itself needs a set-up site to exercise, so this is what guards it: a
		renamed or retyped field on either side breaks the invoice silently, and fails here.
		"""
		subscription_meta = frappe.get_meta("Simple Subscription")
		invoice_meta = frappe.get_meta("Sales Invoice")
		for fieldname, doctype in CUSTOMER_LINK_FIELDS.items():
			with self.subTest(fieldname=fieldname):
				self.assertEqual(subscription_meta.get_field(fieldname).options, doctype)
				self.assertEqual(invoice_meta.get_field(fieldname).options, doctype)


def make_default_address_template() -> None:
	"""Address.validate() renders the address, which needs one. A bare CI site has none."""
	if not frappe.db.exists("Address Template", {"is_default": 1}):
		frappe.get_doc(doctype="Address Template", country="Germany", is_default=1).insert()


def make_customer(name: str) -> str:
	if not frappe.db.exists("Customer", name):
		frappe.get_doc(doctype="Customer", customer_name=name).insert()
	return name


def make_address(title: str, customer: str, line1: str) -> str:
	name = f"{title}-Billing"
	if not frappe.db.exists("Address", name):
		frappe.get_doc(
			doctype="Address",
			address_title=title,
			address_type="Billing",
			address_line1=line1,
			city="Berlin",
			country="Germany",
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
