from simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription import (
	process_subscriptions,
)


def monthly():
	process_subscriptions("Monthly")


def quarterly():
	process_subscriptions("Quarterly")


def halfyearly():
	process_subscriptions("Halfyearly")


def yearly():
	process_subscriptions("Yearly")
