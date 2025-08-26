# Example file with intentional issues for testing

def   badly_formatted_function(  x,y,z  ):
    """missing proper formatting"""
    result=x+y+z
    print('Result is: '+str(result))
    return  result

# Syntax error example (FIXED)
def broken_function():
    print('This is fixed')
    return True

# Undefined name example (FIXED)
def uses_undefined():
    defined_variable = 42  # Fixed: define the variable
    return defined_variable + 1

# Unused import
import os
import sys

def main():
    value = badly_formatted_function(1,2,3)
    print(f"Value: {value}")

if __name__=="__main__":
    main()