def my_decorator(func):
    print("1")
    def wrapper(*args, **kwargs):
        print("Something is happening before the function is called.")
        func(*args, **kwargs)
        print("Something is happening after the function is called.")
    print("2")
    return wrapper

@my_decorator
def say_hello(x):
    print("hello", x)
    
say_hello(5)


# def my_decorator(say_hello):
#     def wrapper():
#         print("Something is happening before the function is called.")
#         say_hello()
#         print("Something is happening after the function is called.")
#     return wrapper