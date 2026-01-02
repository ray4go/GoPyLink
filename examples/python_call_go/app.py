import gopylink

lib = gopylink.load_go_lib("out/go.lib")

# Call Go functions
result = lib.func_call("Hello", "World")
print(result)  # Output: Hello World

result = lib.func_call("Add", 10, 20)
print(result)  # Output: 30

# Create Go type instance and call methods
counter = lib.new_type("Counter", 0)
print(counter.Incr(5))   # Output: 5
print(counter.Incr(3))   # Output: 8
print(counter.Value())   # Output: 8