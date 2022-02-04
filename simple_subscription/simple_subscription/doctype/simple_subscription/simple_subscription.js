// Copyright (c) 2022, ALYF GmbH and contributors
// For license information, please see license.txt

frappe.ui.form.on('Simple Subscription', {
	refresh: function(frm) {
		if (frm.doc.docstatus !== 1) return;

		frm.add_custom_button(__("Create invoice for last month"), () => frappe.call({
			method: "simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription.create_invoice_for_last_month",
			args: {
				subscription_name: frm.doc.name,
			},
			callback: function (r) {
				frm.refresh();
			}
		}));
	}
});
