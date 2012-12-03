#The numerical Python package Numpy contains several functions to optimise matrix
#operations. Using the numpy.vectorize() function it is possible to create an 
#optimised matrix function from a standard function.

# Test each item ('pixel') in a 2d-matrix
#...
# first define a standard non-matrix function...
def value_test(a, b):
    if a <= b:
            return 1
        else:
            return 0
# now vectorize the function
value_test_vect = numpy.vectorize(value_test)
# now pass the new vectorized function the matrix
new_matrix = value_test_vect(matrix, some_value)
#...
