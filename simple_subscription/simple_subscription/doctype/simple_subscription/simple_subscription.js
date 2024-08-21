// Copyright (c) 2022, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on("Simple Subscription", {
	setup: function (frm) {
		frm.set_query("item", "items", function () {
			return {
				filters: {
					is_sales_item: 1,
					has_variants: 0,
				},
			};
		});

		frm.set_query("taxes_and_charges", function (doc) {
			return {
				filters: {
					company: frm.doc.company,
				},
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.disabled === 1) return;

		const translated_frequency = __(
			frm.doc.frequency,
			null,
			"Frequency of Subscription"
		);
		frm.add_custom_button(__("Create last {0} invoice", [translated_frequency]), () =>
			frappe.call({
				method:
					"simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription.create_current_invoice",
				args: {
					subscription_name: frm.doc.name,
				},
				always: function (r) {
					frm.refresh();
				},
			})
		);
	},
});
