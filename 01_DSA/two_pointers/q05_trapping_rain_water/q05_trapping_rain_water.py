"""
Challenge: q05_trapping_rain_water
Difficulty: Hard
Link: https://leetcode.com/problems/trapping-rain-water/

Problem:
Compute how much water can be trapped after raining.
"""

# --- STARTER TEMPLATE FOR USER ---
def trap(height: list[int]) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# For each element in the array, we iterate through the entire array to the left to find the 
# maximum height and the entire array to the right to find the maximum height. 
# The water trapped at the current index is the minimum of these two maximums minus the current height.
def trap_naive(height: list[int]) -> int:
    if not height:
        return 0
    
    n = len(height)
    total_water = 0
    
    for i in range(n):
        left_max = 0
        right_max = 0
        
        # Find the maximum height to the left of index i
        for j in range(i, -1, -1):
            left_max = max(left_max, height[j])
            
        # Find the maximum height to the right of index i
        for j in range(i, n):
            right_max = max(right_max, height[j])
            
        # The water trapped at index i is determined by the shorter of the two boundaries
        total_water += min(left_max, right_max) - height[i]
        
    return total_water

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# This approach uses two pointers moving towards each other. We maintain the maximum height 
# encountered so far from the left and the right. Since the amount of water trapped 
# depends on the minimum of the two boundaries, we can process the side with the smaller 
# current height, knowing that the other side is guaranteed to be at least as tall as 
# the current boundary. This allows us to compute the trapped water in a single pass without 
# extra space for arrays.
def trap_optimal(height: list[int]) -> int:
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    total_water = 0
    
    while left < right:
        if height[left] < height[right]:
            # The bottleneck is on the left side
            if height[left] >= left_max:
                left_max = height[left]
            else:
                total_water += left_max - height[left]
            left += 1
        else:
            # The bottleneck is on the right side
            if height[right] >= right_max:
                right_max = height[right]
            else:
                total_water += right_max - height[right]
            right -= 1
            
    return total_water

# Using the optimal implementation for the required 'trap' signature
def trap(height: list[int]) -> int:
    return trap_optimal(height)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package two_pointers;

public class TrappingRainWater {
    /**
     * Computes the amount of trapped rain water using the two-pointer technique.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int trap(int[] height) {
        if (height == null || height.length == 0) {
            return 0;
        }
        
        int left = 0;
        int right = height.length - 1;
        int leftMax = 0;
        int rightMax = 0;
        int totalWater = 0;
        
        while (left < right) {
            if (height[left] < height[right]) {
                if (height[left] >= leftMax) {
                    leftMax = height[left];
                } else {
                    totalWater += leftMax - height[left];
                }
                left++;
            } else {
                if (height[right] >= rightMax) {
                    rightMax = height[right];
                } else {
                    totalWater += rightMax - height[right];
                }
                right--;
            }
        }
        
        return totalWater;
    }

    public static void main(String[] args) {
        TrappingRainWater solution = new TrappingRainWater();
        int[] height = {0,1,0,2,1,0,1,3,2,1,2,1};
        System.out.println("Trapped Water: " + solution.trap(height)); // Output: 6
    }
}
"""
