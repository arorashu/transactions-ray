
# atexit_simple example

import atexit
import ray
import json


# def without_ray_release():
#     class A:
#         def __init__(self):
#             print("A constructor")
#             atexit.register(self.cleanup)
#
#         def cleanup(self):
#             print("A release resources")
#
#     a = A()


def ray_release():
    @ray.remote
    class B:
        def __init__(self):
            print("B constructor")
            atexit.register(self.cleanup)

        def cleanup(self):
            print("B release resources")
            with open("./examples/cleanup-out.json", "w") as file:
                json.dump({"cleanup": "true"}, file)

        # def __del__(self):
        #     print("B delete release resources")


    ray.init()
    b = B.remote()
    # print("ray complete")


# print("without ray start")
# without_ray_release()
# print("without ray complete")
print("ray start")
ray_release()
print("ray complete")