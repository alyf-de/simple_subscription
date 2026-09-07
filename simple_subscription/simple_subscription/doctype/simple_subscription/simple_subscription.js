// Copyright (c) 2022, ALYF GmbH and contributors
// For license information, please see license.txt

function customer_link_query(frm, query) {
	return {
		query: query,
		filters: { link_doctype: "Customer", link_name: frm.doc.customer },
	};
}

frappe.ui.form.on("Simple Subscription", {
	setup: function (frm) {
		for (const field of ["customer_address", "shipping_address_name"]) {
			frm.set_query(field, () =>
				customer_link_query(frm, "frappe.contacts.doctype.address.address.address_query")
			);
		}

		frm.set_query("contact_person", () =>
			customer_link_query(frm, "frappe.contacts.doctype.contact.contact.contact_query")
		);

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

	customer: function (frm) {
		// address and contact are customer specific, don't keep the previous customer's
		for (const field of ["customer_address", "shipping_address_name", "contact_person"]) {
			frm.set_value(field, null);
		}
	},

	customer_address: function (frm) {
		erpnext.utils.get_address_display(frm, "customer_address", "billing_address_display");
	},

	shipping_address_name: function (frm) {
		erpnext.utils.get_address_display(frm, "shipping_address_name", "shipping_address_display");
	},

	contact_person: function (frm) {
		if (!frm.doc.contact_person) {
			frm.set_value("contact_display", "");
			return;
		}

		frappe.call({
			method: "frappe.contacts.doctype.contact.contact.get_contact_details",
			args: { contact: frm.doc.contact_person },
			callback: (r) => r.message && frm.set_value("contact_display", r.message.contact_display),
		});
	},

	refresh: function (frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.disabled === 1) return;

		const translated_frequency = __(frm.doc.frequency, null, "Frequency of Subscription");
		frm.add_custom_button(__("Create current {0} invoice", [translated_frequency]), () =>
			frappe.call({
				method: "simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription.create_current_invoice",
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
