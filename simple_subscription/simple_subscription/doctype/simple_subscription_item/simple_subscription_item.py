# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock.get_item_details import get_item_details
from erpnext.accounts.party import get_party_details
from frappe.utils import today


class SimpleSubscriptionItem(Document):
	@property
	def current_rate(self):
		parent = frappe.get_doc("Simple Subscription", self.parent)
		currency = parent.currency or frappe.get_cached_value(
			"Company", parent.company, "default_currency"
		)

		party_details = get_party_details(
			party=parent.customer,
			account=None,
			party_type="Customer",
			company=parent.company,
			posting_date=today(),
			currency=currency,
			doctype="Sales Invoice",
			fetch_payment_terms_template=False,
		)

		price_list = (
			party_details.selling_price_list
			or frappe.db.get_single_value("Selling Settings", "selling_price_list")
			or frappe.db.get_value(
				"Price List", {"selling": 1, "currency": currency, "enabled": 1}
			)
		)

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
