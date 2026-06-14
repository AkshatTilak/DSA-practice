"""
Challenge: q07_longest_consecutive_sequence
Difficulty: Medium
Link: https://leetcode.com/problems/longest-consecutive-sequence/

Problem:
Find the length of the longest consecutive elements sequence in O(N).
"""

# --- STARTER TEMPLATE FOR USER ---
def longest_consecutive(nums: list[int]) -> int: 
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N log N)
# Space Complexity: O(N)
# The naive approach involves sorting the array first. Once sorted, we can iterate through the array 
# and count the length of consecutive elements. We handle duplicates by skipping them.
def longest_consecutive_naive(nums: list[int]) -> int:
    if not nums:
        return 0
    
    # Sorting takes O(N log N)
    nums.sort()
    
    longest_streak = 1
    current_streak = 1
    
    for i in range(1, len(nums)):
        # Skip duplicates
        if nums[i] == nums[i-1]:
            continue
        
        # Check if current element is consecutive to the previous one
        if nums[i] == nums[i-1] + 1:
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1
            
    return max(longest_streak, current_streak)

# --- APPROACH 2: Optimal (Hash Set) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach uses a hash set to allow O(1) lookups. We only start counting a sequence if the 
# current number is the actual start of a sequence (i.e., num - 1 is not in the set). 
# This ensures that each element is visited at most twice, resulting in linear time complexity.
def longest_consecutive_optimal(nums: list[int]) -> int:
    # Convert list to set for O(1) lookups
    num_set = set(nums)
    longest_streak = 0
    
    for num in num_set:
        # Only start building a sequence if 'num' is the beginning of a sequence
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1
            
            # Increment the sequence length as long as the next consecutive number exists
            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1
            
            longest_streak = max(longest_streak, current_streak)
            
    return longest_streak

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.HashSet;
import java.util.Set;

public class LongestConsecutiveSequence {
    /**
     * Finds the length of the longest consecutive elements sequence.
     * Time Complexity: O(N)
     * Space Complexity: O(N)
     */
    public int longestConsecutive(int[] nums) {
        if (nums == null || nums.length == 0) {
            return 0;
        }

        Set<Integer> numSet = new HashSet<>();
        for (int num : nums) {
            numSet.add(num);
        }

        int longestStreak = 0;

        for (int num : numSet) {
            // Check if 'num' is the start of a sequence
            if (!numSet.contains(num - 1)) {
                int currentNum = num;
                int currentStreak = 1;

                while (numSet.contains(currentNum + 1)) {
                    currentNum += 1;
                    currentStreak += 1;
                }

                longestStreak = Math.max(longestStreak, currentStreak);
            }
        }

        return longestStreak;
    }

    public static void main(String[] args) {
        LongestConsecutiveSequence solver = new LongestConsecutiveSequence();
        int[] nums = {100, 4, 200, 1, 3, 2};
        System.out.println("Longest sequence length: " + solver.longestConsecutive(nums)); // Expected: 4
    }
}
"""
