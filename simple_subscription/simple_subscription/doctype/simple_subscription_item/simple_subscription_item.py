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

		party_details = get_party_details(
			party=parent.customer,
			account=None,
			party_type="Customer",
			company=parent.company,
			posting_date=today(),
			currency=parent.currency,
			doctype="Sales Invoice",
			fetch_payment_terms_template=False,
		)

		item_details = get_item_details(
			{
				"item_code": self.item,
				"company": parent.company,
				"doctype": "Sales Invoice",
				"currency": parent.currency,
				"price_list_currency": parent.currency,
				"qty": self.qty,
				"plc_conversion_rate": 1,
				"conversion_rate": 1,
				"customer": parent.customer,
				"transaction_date": today(),
				"price_list": party_details.selling_price_list,
			}
		)
		return item_details.price_list_rate - (item_details.discount_amount or 0)

	@property
	def current_description(self):
		return frappe.db.get_value("Item", self.item, "description")

	@property
	def item_name(self):
		item = frappe.get_doc("Item", self.item)
		return item.item_name
