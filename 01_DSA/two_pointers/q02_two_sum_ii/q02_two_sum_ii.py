"""
Challenge: q02_two_sum_ii
Difficulty: Medium
Link: https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

Problem:
Find two numbers in a sorted array that add up to target.
"""

# --- STARTER TEMPLATE FOR USER ---
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach uses nested loops to check every possible pair of numbers in the array.
# Although simple, it is inefficient for large arrays as it does not leverage the sorted property of the input.
def two_sum_sorted_naive(numbers: list[int], target: int) -> list[int]:
    n = len(numbers)
    for i in range(n):
        for j in range(i + 1, n):
            if numbers[i] + numbers[j] == target:
                # Returning 1-based indices as per standard Two Sum II specifications
                return [i + 1, j + 1]
    return []

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# Since the input array is already sorted, we can use two pointers: one at the beginning and one at the end.
# If the sum is too small, we move the left pointer forward to increase the sum.
# If the sum is too large, we move the right pointer backward to decrease the sum.
# This is optimal because it processes the array in a single pass and requires no additional memory.
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    left = 0
    right = len(numbers) - 1
    
    while left < right:
        current_sum = numbers[left] + numbers[right]
        
        if current_sum == target:
            return [left + 1, right + 1]
        elif current_sum < target:
            left += 1
        else:
            right -= 1
            
    return []

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package two_pointers;

public class TwoSumIi {
    /**
     * Finds two numbers in a sorted array that add up to a specific target.
     * Returns the 1-based indices of the two numbers.
     * 
     * @param numbers Sorted array of integers
     * @param target The target sum
     * @return int array containing 1-based indices [index1, index2]
     */
    public int[] twoSum(int[] numbers, int target) {
        int left = 0;
        int right = numbers.length - 1;
        
        while (left < right) {
            int currentSum = numbers[left] + numbers[right];
            
            if (currentSum == target) {
                return new int[]{left + 1, right + 1};
            } else if (currentSum < target) {
                left++;
            } else {
                right--;
            }
        }
        
        // Return an empty array if no solution is found, although problem 
        // constraints typically guarantee exactly one solution.
        return new int[0];
    }

    public static void main(String[] args) {
        TwoSumIi solution = new TwoSumIi();
        int[] nums = {2, 7, 11, 15};
        int target = 9;
        int[] result = solution.twoSum(nums, target);
        System.out.println("[" + result[0] + ", " + result[1] + "]"); // Expected: [1, 2]
    }
}
"""
