"""
Challenge: q06_largest_rectangle_in_histogram
Difficulty: Hard
Link: https://leetcode.com/problems/largest-rectangle-in-histogram/

Problem:
Find the area of largest rectangle in histogram.
"""

# --- STARTER TEMPLATE FOR USER ---
def largest_rectangle_area(heights: list[int]) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(1)
# For every bar, we treat it as the minimum height of a potential rectangle and 
# expand outwards to the left and right as long as the adjacent bars are 
# greater than or equal to the current bar's height.
def largest_rectangle_area_naive(heights: list[int]) -> int:
    if not heights:
        return 0
    
    max_area = 0
    n = len(heights)
    
    for i in range(n):
        # Current bar is the shortest bar in the rectangle
        min_h = heights[i]
        
        # Expand to the left
        left = i
        while left > 0 and heights[left - 1] >= min_h:
            left -= 1
            
        # Expand to the right
        right = i
        while right < n - 1 and heights[right + 1] >= min_h:
            right += 1
            
        width = right - left + 1
        max_area = max(max_area, width * min_h)
        
    return max_area

# --- APPROACH 2: Optimal (Monotonic Stack) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# The optimal approach uses a monotonic increasing stack to keep track of indices of heights.
# When we encounter a height smaller than the top of the stack, we know the rectangle 
# rooted at the top index cannot extend further right. We pop it and calculate the area 
# using the current index as the right boundary and the index below it in the stack 
# as the left boundary. This ensures each element is pushed and popped exactly once.
def largest_rectangle_area_optimal(heights: list[int]) -> int:
    if not heights:
        return 0
    
    stack = [] # Stores indices
    max_area = 0
    # Append a 0 height to the end to ensure all remaining elements in the stack 
    # are processed at the end of the loop.
    heights_extended = heights + [0]
    
    for i, h in enumerate(heights_extended):
        # Maintain a monotonic increasing stack
        while stack and heights_extended[stack[-1]] >= h:
            # The bar at stack[-1] is the height of the rectangle
            height = heights_extended[stack.pop()]
            # The width is determined by the current index i (right boundary)
            # and the new top of the stack (left boundary)
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        
        stack.append(i)
        
    return max_area

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package stack;

import java.util.Stack;

public class LargestRectangleInHistogram {
    /**
     * Calculates the area of the largest rectangle in a histogram.
     * Time Complexity: O(N)
     * Space Complexity: O(N)
     */
    public int largestRectangleArea(int[] heights) {
        if (heights == null || heights.length == 0) {
            return 0;
        }

        Stack<Integer> stack = new Stack<>();
        int maxArea = 0;
        int n = heights.length;

        for (int i = 0; i <= n; i++) {
            // Use 0 as the height for the virtual element at index n to clear the stack
            int currentHeight = (i == n) ? 0 : heights[i];

            while (!stack.isEmpty() && heights[stack.peek()] >= currentHeight) {
                int h = heights[stack.pop()];
                int width = stack.isEmpty() ? i : i - stack.peek() - 1;
                maxArea = Math.max(maxArea, h * width);
            }
            stack.push(i);
        }

        return maxArea;
    }

    public static void main(String[] args) {
        LargestRectangleInHistogram solver = new LargestRectangleInHistogram();
        int[] test1 = {2, 1, 5, 6, 2, 3};
        System.out.println("Test 1: " + solver.largestRectangleArea(test1)); // Expected: 10
        
        int[] test2 = {2, 4};
        System.out.println("Test 2: " + solver.largestRectangleArea(test2)); // Expected: 4
    }
}
"""

# To maintain consistency with the starter code's required function name:
def largest_rectangle_area(heights: list[int]) -> int:
    return largest_rectangle_area_optimal(heights)
