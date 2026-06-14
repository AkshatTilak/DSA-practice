"""
Challenge: q05_daily_temperatures
Difficulty: Medium
Link: https://leetcode.com/problems/daily-temperatures/

Problem:
Return an array showing days to wait for a warmer temperature.
"""

# --- STARTER TEMPLATE FOR USER ---
def daily_temperatures(temperatures: list[int]) -> list[int]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(1)
# For every day, we iterate through the remaining days to find the first occurrence of a higher temperature.
def daily_temperatures_naive(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    result = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                result[i] = j - i
                break
    return result

# --- APPROACH 2: Optimal (Monotonic Stack) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# We maintain a monotonic decreasing stack of indices. When we encounter a temperature 
# warmer than the temperature at the index on top of the stack, we have found the 
# next warmer day for that index. Each element is pushed and popped from the stack exactly once.
def daily_temperatures_optimal(temperatures: list[int]) -> list[int]:
    n = len(temperatures)
    result = [0] * n
    stack = []  # Stores indices of temperatures
    
    for i in range(n):
        # While stack is not empty and current temperature is warmer than the temperature 
        # at the index stored at the top of the stack
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_index = stack.pop()
            result[prev_index] = i - prev_index
        stack.append(i)
        
    return result

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package stack;

import java.util.ArrayDeque;
import java.util.Deque;

public class DailyTemperatures {
    /**
     * Returns an array showing the number of days to wait for a warmer temperature.
     * Uses a monotonic stack to achieve linear time complexity.
     */
    public int[] dailyTemperatures(int[] temperatures) {
        int n = temperatures.length;
        int[] result = new int[n];
        // Deque is preferred over Stack class in Java for better performance
        Deque<Integer> stack = new ArrayDeque<>();

        for (int i = 0; i < n; i++) {
            while (!stack.isEmpty() && temperatures[i] > temperatures[stack.peek()]) {
                int prevIndex = stack.pop();
                result[prevIndex] = i - prevIndex;
            }
            stack.push(i);
        }

        return result;
    }

    public static void main(String[] args) {
        DailyTemperatures solver = new DailyTemperatures();
        int[] temps = {73, 74, 75, 71, 69, 72, 76, 73};
        int[] result = solver.dailyTemperatures(temps);
        
        for (int val : result) {
            System.out.print(val + " ");
        }
        // Expected output: 1 1 4 2 1 1 0 0 
    }
}
"""
