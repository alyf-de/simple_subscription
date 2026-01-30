# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.get_item_details import get_item_details
from frappe.model.document import Document
from frappe.utils import today


class SimpleSubscriptionItem(Document):
	@property
	def current_rate(self):
		parent = frappe.get_doc("Simple Subscription", self.parent)
		currency = parent.currency or frappe.get_cached_value("Company", parent.company, "default_currency")

		price_list = parent.get_price_list()

		item_details = get_item_details(
			{
				"item_code": self.item,
				"company": parent.company,
				"doctype": "Sales Invoice",
				"currency": currency,
				"price_list_currency": currency,
				"qty": self.qty,
				"plc_conversion_rate": 1,
				"conversion_rate": 1,
				"customer": parent.customer,
				"transaction_date": today(),
				"price_list": price_list,
			}
		)
		return item_details.price_list_rate - (item_details.discount_amount or 0)

	@property
	def current_description(self):
		return frappe.db.get_value("Item", self.item, "description")

	@property
	def item_name(self):
		return frappe.db.get_value("Item", self.item, "item_name")
