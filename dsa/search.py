"""Linear search and dictionary lookup for transactions by ID"""

def linear_search(transactions_list, target_id):
    target = str(target_id)
    for transaction in transactions_list:
        if transaction.get("id") == target:
            return transaction
    return None


def dict_search(transactions_dict, target_id):
    return transactions_dict.get(str(target_id))


if __name__ == "__main__":
    from dsa.store import get_default_store

    store = get_default_store()
    test_id = store.transaction_list[10]["id"]
    missing_id = "00000"

    print(f"Search test id: {test_id}")
    print(f"Linear: {linear_search(store.transaction_list, test_id) is not None}")
    print(f"Dict:   {dict_search(store.transaction_dict, test_id) is not None}")
    print(f"\nResult:   {dict_search(store.transaction_dict, test_id)}")
    print(f"\nSearch missing id: {missing_id}")
    print(f"Missing id linear: {linear_search(store.transaction_list, missing_id)}")
    print(f"Missing id dict:   {dict_search(store.transaction_dict, missing_id)}")
