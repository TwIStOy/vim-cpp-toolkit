import cpp_toolkit.switch as switch
import os

print(switch._has_sub_directory(os.getcwd(), 'python'))
print(switch._replace_sub_directory(os.getcwd(), ['autoload', 'cpp_toolkit'], ['src', 'py', 'fuck']))

