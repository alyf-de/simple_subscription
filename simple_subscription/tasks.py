from simple_subscription.simple_subscription.doctype.simple_subscription.simple_subscription import (
	process_subscriptions, Frequency
)


def monthly():
	process_subscriptions(Frequency.Monthly)


def quarterly():
	process_subscriptions(Frequency.Quarterly)


def halfyearly():
	process_subscriptions(Frequency.Halfyearly)


def yearly():
	process_subscriptions(Frequency.Yearly)
