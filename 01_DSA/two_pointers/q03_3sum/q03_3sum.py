"""
Challenge: q03_3sum
Difficulty: Medium
Link: https://leetcode.com/problems/3sum/

Problem:
Find all unique triplets that sum to zero.
"""

# --- STARTER TEMPLATE FOR USER ---
def three_sum(nums: list[int]) -> list[list[int]]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^3)
# Space Complexity: O(M) where M is the number of unique triplets
# This approach uses three nested loops to check every possible combination of three elements. 
# To ensure uniqueness of triplets, we sort each found triplet and store it in a set.
def three_sum_naive(nums: list[int]) -> list[list[int]]:
    res = set()
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if nums[i] + nums[j] + nums[k] == 0:
                    # Sort the triplet to handle duplicates via the set
                    triplet = tuple(sorted([nums[i], nums[j], nums[k]]))
                    res.add(triplet)
    return [list(t) for t in res]

# --- APPROACH 2: Optimal (Sorting + Two Pointers) ---
# Time Complexity: O(N^2)
# Space Complexity: O(1) or O(N) depending on the sorting implementation
# This approach is optimal because it reduces the search space from O(N^3) to O(N^2). 
# By sorting the array, we can use two pointers (left and right) to find the target sum 
# for a fixed element nums[i]. Skipping identical elements ensures that no duplicate 
# triplets are added to the result without needing a costly set operation.
def three_sum_optimal(nums: list[int]) -> list[list[int]]:
    nums.sort()
    res = []
    n = len(nums)
    
    for i in range(n - 2):
        # Skip duplicate values for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        # Optimization: Since the array is sorted, if nums[i] > 0, 
        # no three numbers can sum to 0
        if nums[i] > 0:
            break
            
        left, right = i + 1, n - 1
        while left < right:
            current_sum = nums[i] + nums[left] + nums[right]
            if current_sum == 0:
                res.append([nums[i], nums[left], nums[right]])
                # Skip duplicate values for the second and third elements
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current_sum < 0:
                left += 1
            else:
                right -= 1
                
    return res

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package two_pointers;

import java.util.*;

public class ThreeSum {
    /**
     * Finds all unique triplets that sum to zero.
     * Time Complexity: O(N^2)
     * Space Complexity: O(1) (excluding the space for the output list)
     */
    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        if (nums == null || nums.length < 3) {
            return result;
        }

        Arrays.sort(nums);

        for (int i = 0; i < nums.length - 2; i++) {
            // Avoid duplicates for the first element
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }

            // Optimization: If the smallest number is > 0, sum cannot be 0
            if (nums[i] > 0) {
                break;
            }

            int left = i + 1;
            int right = nums.length - 1;

            while (left < right) {
                int sum = nums[i] + nums[left] + nums[right];

                if (sum == 0) {
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));

                    // Avoid duplicates for left and right pointers
                    while (left < right && nums[left] == nums[left + 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right - 1]) {
                        right--;
                    }
                    left++;
                    right--;
                } else if (sum < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return result;
    }
}
"""
