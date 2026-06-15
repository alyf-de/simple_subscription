// Copyright (c) 2022, ALYF GmbH and contributors
// For license information, please see license.txt

const ALL_FREQUENCIES = ["Monthly", "Quarterly", "Halfyearly", "Yearly", "Biennial", "Triennial"];
const START_DATE_ONLY_FREQUENCIES = ["Biennial", "Triennial"];

function set_frequency_options(frm) {
	const options =
		frm.doc.period_type === "calendar months"
			? ALL_FREQUENCIES.filter((frequency) => !START_DATE_ONLY_FREQUENCIES.includes(frequency))
			: ALL_FREQUENCIES;

	if (
		frm.doc.period_type === "calendar months" &&
		START_DATE_ONLY_FREQUENCIES.includes(frm.doc.frequency)
	) {
		frm.set_value("frequency", "");
	}

	frm.set_df_property("frequency", "options", options.join("\n"));
}

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

	period_type: function (frm) {
		set_frequency_options(frm);
	},

	refresh: function (frm) {
		set_frequency_options(frm);

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
