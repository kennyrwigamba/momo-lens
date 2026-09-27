# Search Algorithms: Linear Search vs Dictionary Lookup

# Linear search: checks each transaction in the list one by one until it finds the ID
def linear_search(transactions_list, target_id):
    target = str(target_id)
    for transaction in transactions_list:
        if transaction.get("id") == target:
            return transaction
    return None


# Dictionary search: direct lookup using hash key in O(1) constant time
def dict_search(transactions_dict, target_id):
    return transactions_dict.get(str(target_id))


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Add project root to sys.path
    ROOT_DIR = Path(__file__).resolve().parent.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    from dsa.store import get_default_store

    store = get_default_store()
    test_id = store.list[10]["id"]

    print(f"Testing search for ID: {test_id}")

    # Test linear search
    linear_result = linear_search(store.list, test_id)
    print(f"Linear search found: {linear_result is not None}")

    # Test dict search
    dict_result = dict_search(store.dict, test_id)
    print(f"Dict search found:   {dict_result is not None}")

    # Test missing ID
    missing_id = "NON_EXISTENT_ID_99999"
    print(f"Testing missing ID: {missing_id}")
    print(f"Linear search result: {linear_search(store.list, missing_id)}")
    print(f"Dict search result:   {dict_search(store.dict, missing_id)}")
