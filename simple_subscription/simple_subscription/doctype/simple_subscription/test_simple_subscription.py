# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

# import frappe
import unittest
from datetime import date

from .simple_subscription import (
	get_first_day_of_period,
	get_period_start_and_end_dates,
	Frequency,
)


class TestSimpleSubscription(unittest.TestCase):
	def test_get_first_day_of_period(self):
		from_date = date(2022, 11, 7)

		invoice_date = get_first_day_of_period(from_date, Frequency.Monthly)
		self.assertEqual(invoice_date, date(2022, 11, 1))

		invoice_date = get_first_day_of_period(from_date, Frequency.Quarterly)
		self.assertEqual(invoice_date, date(2022, 10, 1))

		invoice_date = get_first_day_of_period(from_date, Frequency.Halfyearly)
		self.assertEqual(invoice_date, date(2022, 7, 1))

		invoice_date = get_first_day_of_period(from_date, Frequency.Yearly)
		self.assertEqual(invoice_date, date(2022, 1, 1))

	def test_get_period_start_and_end_dates(self):
		invoice_date = date(2022, 2, 1)
		start_date, end_date = get_period_start_and_end_dates(
			invoice_date, Frequency.Monthly
		)
		self.assertEqual(start_date, date(2022, 1, 1))
		self.assertEqual(end_date, date(2022, 1, 31))

		invoice_date = date(2022, 1, 1)
		start_date, end_date = get_period_start_and_end_dates(
			invoice_date, Frequency.Quarterly
		)
		self.assertEqual(start_date, date(2021, 10, 1))
		self.assertEqual(end_date, date(2021, 12, 31))

		invoice_date = date(2022, 1, 1)
		start_date, end_date = get_period_start_and_end_dates(
			invoice_date, Frequency.Halfyearly
		)
		self.assertEqual(start_date, date(2021, 7, 1))
		self.assertEqual(end_date, date(2021, 12, 31))

		invoice_date = date(2022, 1, 1)
		start_date, end_date = get_period_start_and_end_dates(
			invoice_date, Frequency.Yearly
		)
		self.assertEqual(start_date, date(2021, 1, 1))
		self.assertEqual(end_date, date(2021, 12, 31))
