# Copyright (c) 2022, ALYF GmbH and Contributors
# See license.txt

# import frappe
import unittest
from datetime import date

from .simple_subscription import (
	get_calendar_period,
	get_date_period,
	Frequency,
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

