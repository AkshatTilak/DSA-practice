"""
Challenge: q08_find_duplicate
Difficulty: Medium
Link: https://leetcode.com/problems/find-the-duplicate-number/

Problem:
Find duplicate using cycle detection.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n) or O(1) depending on sorting implementation
# This approach sorts the input list and then iterates through it to find two adjacent elements that are identical.
def solve_naive(nums):
    if not nums:
        return None
    
    # Create a sorted copy to avoid modifying the original input if necessary,
    # though standard naive sorting usually takes O(n log n).
    sorted_nums = sorted(nums)
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i] == sorted_nums[i + 1]:
            return sorted_nums[i]
    return None

# --- APPROACH 2: Optimal (Floyd's Cycle Finding Algorithm) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach treats the array as a linked list where the value at index 'i' points to the index 'nums[i]'.
# Since there is a duplicate, a cycle must exist. Floyd's Tortoise and Hare algorithm is used to:
# 1. Detect the cycle using a slow and fast pointer.
# 2. Find the start of the cycle, which corresponds to the duplicate number.
# It is optimal because it requires no extra space and performs the search in linear time without modifying the input array.
def solve_optimal(nums):
    if not nums:
        return None
        
    # Phase 1: Detecting the cycle
    # Initialize slow and fast pointers.
    # We start from the first element.
    slow = nums[0]
    fast = nums[0]
    
    # Move slow pointer by 1 step and fast pointer by 2 steps until they meet.
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
            
    # Phase 2: Finding the entrance to the cycle (the duplicate)
    # Reset one pointer to the start of the array.
    slow = nums[0]
    # Move both pointers at the same speed until they meet.
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
        
    return slow

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package linked_list;

public class FindDuplicate {
    /**
     * Finds the duplicate number in an array of n+1 integers where each integer is between 1 and n.
     * Implements Floyd's Cycle Finding Algorithm.
     * 
     * @param nums Input array
     * @return The duplicate number
     */
    public int solveOptimal(int[] nums) {
        if (nums == null || nums.length == 0) {
            throw new IllegalArgumentException("Array must not be empty");
        }

        // Phase 1: Find the intersection point of the two pointers.
        int slow = nums[0];
        int fast = nums[0];

        do {
            slow = nums[slow];
            fast = nums[nums[fast]];
        } while (slow != fast);

        // Phase 2: Find the entrance to the cycle.
        slow = nums[0];
        while (slow != fast) {
            slow = nums[slow];
            fast = nums[fast];
        }

        return slow;
    }

    public static void main(String[] args) {
        FindDuplicate fd = new FindDuplicate();
        int[] test1 = {1, 3, 4, 2, 2};
        int[] test2 = {3, 1, 3, 4, 2};
        System.out.println("Duplicate 1: " + fd.solveOptimal(test1)); // Expected: 2
        System.out.println("Duplicate 2: " + fd.solveOptimal(test2)); // Expected: 3
    }
}
"""
