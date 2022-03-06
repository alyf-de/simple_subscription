# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

# import frappe
import unittest
from datetime import date

from .simple_subscription import (
	get_first_day_of_period,
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
