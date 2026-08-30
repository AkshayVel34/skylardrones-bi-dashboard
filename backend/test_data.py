from monday_data import get_deals, get_work_orders


print("Fetching Deals...")

deals = get_deals()

print("Deals:", len(deals))


print("\nFetching Work Orders...")

work_orders = get_work_orders()

print("Work Orders:", len(work_orders))