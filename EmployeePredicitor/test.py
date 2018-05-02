def matrixReshape(nums, r, c):
    """
    :type nums: List[List[int]]
    :type r: int
    :type c: int
    :rtype: List[List[int]]
    """
    len_2 = len(nums)
    len_1 = len(nums[0])
    size_n = len_2 * len_1
    if not r*c == size_n:
        return nums
    else:
        flatten_ls = [j for i in nums for j in i]
        r_list =  []            
        for i in range(0,r):
            r_list.append(flatten_ls[i*c:(i+1)*c])
        return r_list

if __name__ == "__main__" :
    nums = [[1,2],[3,4]]
    r = 4
    c = 1
    matrixReshape(nums, r, c)