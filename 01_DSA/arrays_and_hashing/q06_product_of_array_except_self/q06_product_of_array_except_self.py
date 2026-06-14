"""
Challenge: q06_product_of_array_except_self
Difficulty: Medium
Link: https://leetcode.com/problems/product-of-array-except-self/

Problem:
Return an array where each index is the product of all elements except the one at that index, without using division.
"""

# --- STARTER TEMPLATE FOR USER ---
def product_except_self(nums: list[int]) -> list[int]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach iterates through each element and calculates the product of all other elements using a nested loop.
def product_except_self_naive(nums: list[int]) -> list[int]:
    n = len(nums)
    res = [1] * n
    for i in range(n):
        current_product = 1
        for j in range(n):
            if i != j:
                current_product *= nums[j]
        res[i] = current_product
    return res

# --- APPROACH 2: Optimal (Prefix and Suffix Products) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach calculates prefix products in a first pass and suffix products in a second pass. 
# By reusing the result array to store prefixes and calculating suffixes on the fly, we achieve O(1) extra space.
# This is optimal because we must visit every element at least once, and we use the minimum possible auxiliary space.
def product_except_self_optimal(nums: list[int]) -> list[int]:
    n = len(nums)
    res = [1] * n
    
    # Step 1: Calculate prefix products
    # res[i] will contain the product of all elements to the left of index i
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= nums[i]
        
    # Step 2: Calculate suffix products and multiply with prefix products
    # suffix will maintain the product of all elements to the right of index i
    suffix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suffix
        suffix *= nums[i]
        
    return res

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

public class ProductOfArrayExceptSelf {
    /**
     * Calculates the product of all elements except the one at the current index.
     * Time Complexity: O(n)
     * Space Complexity: O(1) excluding the output array.
     */
    public int[] productExceptSelf(int[] nums) {
        int n = nums.length;
        int[] res = new int[n];
        
        // Left pass: Compute prefix products
        int prefix = 1;
        for (int i = 0; i < n; i++) {
            res[i] = prefix;
            prefix *= nums[i];
        }
        
        // Right pass: Compute suffix products and multiply
        int suffix = 1;
        for (int i = n - 1; i >= 0; i--) {
            res[i] *= suffix;
            suffix *= nums[i];
        }
        
        return res;
    }

    public static void main(String[] args) {
        ProductOfArrayExceptSelf solver = new ProductOfArrayExceptSelf();
        int[] input = {1, 2, 3, 4};
        int[] result = solver.productExceptSelf(input);
        for (int val : result) {
            System.out.print(val + " ");
        }
        // Expected Output: 24 12 8 6 
    }
}
"""
