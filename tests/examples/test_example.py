# Example file with intentional issues for testing

def   badly_formatted_function(  x,y,z  ):
    """missing proper formatting"""
    result=x+y+z
    print('Result is: '+str(result))
    return  result

# Syntax error example
def broken_function():
    print('This is broken'
    return True

# Undefined name example  
def uses_undefined():
    return undefined_variable + 1

# Unused import
import os
import sys

def main():
    value = badly_formatted_function(1,2,3)
    print(f"Value: {value}")

if __name__=="__main__":
    main()