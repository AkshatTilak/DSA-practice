"""
Challenge: q04_container_with_most_water
Difficulty: Medium
Link: https://leetcode.com/problems/container-with-most-water/

Problem:
Find two lines that contain the most water.
"""

# --- STARTER TEMPLATE FOR USER ---
def max_area(height: list[int]) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2)
# Space Complexity: O(1)
# This approach iterates through every possible pair of lines to calculate the area and finds the maximum.
def max_area_naive(height: list[int]) -> int:
    max_v = 0
    n = len(height)
    for i in range(n):
        for j in range(i + 1, n):
            # Area = minimum height of the two boundaries * distance between them
            current_area = min(height[i], height[j]) * (j - i)
            if current_area > max_v:
                max_v = current_area
    return max_v

# --- APPROACH 2: Optimal (Two Pointers) ---
# Time Complexity: O(n)
# Space Complexity: O(1)
# The optimal approach uses two pointers starting at the opposite ends of the array. 
# We move the pointer pointing to the shorter line inward because the area is limited by the 
# shorter boundary; moving the taller boundary would only decrease the width without 
# any possibility of increasing the height of the container.
def max_area_optimal(height: list[int]) -> int:
    left = 0
    right = len(height) - 1
    max_v = 0
    
    while left < right:
        # Calculate area with current pointers
        h_left = height[left]
        h_right = height[right]
        current_area = min(h_left, h_right) * (right - left)
        
        if current_area > max_v:
            max_v = current_area
            
        # Move the pointer that points to the shorter line
        if h_left < h_right:
            left += 1
        else:
            right -= 1
            
    return max_v

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package two_pointers;

public class ContainerWithMostWater {
    /**
     * Calculates the maximum amount of water a container can store.
     * Time Complexity: O(n)
     * Space Complexity: O(1)
     */
    public int maxArea(int[] height) {
        if (height == null || height.length < 2) {
            return 0;
        }
        
        int left = 0;
        int right = height.length - 1;
        int maxWater = 0;
        
        while (left < right) {
            int leftHeight = height[left];
            int rightHeight = height[right];
            
            // Area = min(h1, h2) * width
            int currentArea = Math.min(leftHeight, rightHeight) * (right - left);
            maxWater = Math.max(maxWater, currentArea);
            
            // Move the pointer of the shorter wall to potentially find a taller wall
            if (leftHeight < rightHeight) {
                left++;
            } else {
                right--;
            }
        }
        
        return maxWater;
    }

    public static void main(String[] args) {
        ContainerWithMostWater solver = new ContainerWithMostWater();
        int[] heights = {1, 8, 6, 2, 5, 4, 8, 3, 7};
        System.out.println("Max Water: " + solver.maxArea(heights)); // Expected: 49
    }
}
"""
