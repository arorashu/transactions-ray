import ray


@ray.remote
class ServiceClass:
    def __init__(self, store):
        print(f"constructor args: {store}")
        self.store = store

    def get_store(self):
        return self.store

    def add_pair(self, key, value):
        # store = ray.get(self.store_handle)
        self.store[key] = value
        # self.store_handle = ray.put(store)
        return True


ray.init()
store = {
    "key1": "value1"
}
store2 = {
    "k1": "v1"
}
store_handle = ray.put(store)
# print(f"store2_handle: {store2_handle}")

service = ServiceClass.remote(store_handle)
# cur_store = ray.get(service.get_store.remote())
# cur_store_handle = ray.get(service.get_store.remote())
# print(f"current_store_handle: {cur_store_handle}")
print(f"current_store: {ray.get(service.get_store.remote())}")

is_added = ray.get(service.add_pair.remote("key2", "value2"))
print(f"is added: {is_added}")
print(f"current_store: {ray.get(service.get_store.remote())}")

print(f"current_store from handle: {ray.get(store_handle)}")

# cur_store_handle = ray.get(service.get_store.remote())
# print(f"current_store_handle: {cur_store_handle}")
# print(f"current_store: {ray.get(cur_store_handle)}")

# TODO: how to keep a handle consistent among various actors?

