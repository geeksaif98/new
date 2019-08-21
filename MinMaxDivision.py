"""
You are given integers K, M and a non-empty array A consisting of N integers. Every element of the array is not greater than M.

You should divide this array into K blocks of consecutive elements. The size of the block is any integer between 0 and N. Every element of the array should belong to some block.

The sum of the block from X to Y equals A[X] + A[X + 1] + ... + A[Y]. The sum of empty block equals 0.

The large sum is the maximal sum of any block.

For example, you are given integers K = 3, M = 5 and array A such that:

  A[0] = 2
  A[1] = 1
  A[2] = 5
  A[3] = 1
  A[4] = 2
  A[5] = 2
  A[6] = 2
The array can be divided, for example, into the following blocks:

[2, 1, 5, 1, 2, 2, 2], [], [] with a large sum of 15;
[2], [1, 5, 1, 2], [2, 2] with a large sum of 9;
[2, 1, 5], [], [1, 2, 2, 2] with a large sum of 8;
[2, 1], [5, 1], [2, 2, 2] with a large sum of 6.
The goal is to minimize the large sum. In the above example, 6 is the minimal large sum.

Write a function:

def solution(K, M, A)

that, given integers K, M and a non-empty array A consisting of N integers, returns the minimal large sum.

For example, given K = 3, M = 5 and array A such that:

  A[0] = 2
  A[1] = 1
  A[2] = 5
  A[3] = 1
  A[4] = 2
  A[5] = 2
  A[6] = 2
the function should return 6, as explained above.

Write an efficient algorithm for the following assumptions:

N and K are integers within the range [1..100,000];
M is an integer within the range [0..10,000];
each element of array A is an integer within the range [0..M].

"""
"""
    this function check is there a bunch of numbers which their sum are equal to the (mid) parameter
"""


array = [2, 1, 9, 1, 2, 3, 3]
global sum_history
sum_history = 0
def find_nums_sum_equal_mid(mid,start=0,element_index=0):
    global sum_history
    if array.index(array[element_index]) == array.index(array[-1]):
        return None
    else:
        sum_of_start_and_next_element = array[start] + array[start + 1] + sum_history
        
        if sum_of_start_and_next_element == mid:
            large_max_sum_block = array[element_index:start+2]
            indices = [i for i in range(element_index,start+2)]
            rest_of_elements = [i for j, i in enumerate(array) if j not in indices]

            print(large_max_sum_block)
            print(rest_of_elements)


        elif sum_of_start_and_next_element < mid:
            sum_history += array[start]
            start += 1
            return find_nums_sum_equal_mid(mid,start,element_index)
        elif sum_of_start_and_next_element > mid:
            element_index += 1
            start = element_index
            sum_history = 0
            return find_nums_sum_equal_mid(mid,start,element_index)


find_nums_sum_equal_mid(5)


























