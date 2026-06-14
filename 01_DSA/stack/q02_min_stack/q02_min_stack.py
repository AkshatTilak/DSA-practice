"""
Challenge: q02_min_stack
Difficulty: Medium
Link: https://leetcode.com/problems/min-stack/

Problem:
Design a stack that supports push, pop, top, and retrieving the minimum element in O(1).
"""

# --- STARTER TEMPLATE FOR USER ---
class MinStack:
    def __init__(self):
        pass
    def push(self, val: int) -> None:
        pass
    def pop(self) -> None:
        pass
    def top(self) -> int:
        pass
    def getMin(self) -> int:
        pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1) for push, pop, top; O(n) for getMin
# Space Complexity: O(n)
# In the naive approach, we use a standard list as a stack. While push, pop, and top operations are efficient, 
# the getMin operation requires iterating through the entire stack to find the minimum element, resulting in linear time complexity.
class MinStack_naive:
    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)

    def pop(self) -> None:
        if self.stack:
            self.stack.pop()

    def top(self) -> int:
        return self.stack[-1] if self.stack else None

    def getMin(self) -> int:
        return min(self.stack) if self.stack else None

# --- APPROACH 2: Optimal (Auxiliary Min-Stack) ---
# Time Complexity: O(1) for all operations
# Space Complexity: O(n)
# This approach is optimal because it maintains a secondary stack (min_stack) that tracks the minimum 
# element corresponding to every state of the main stack. By pushing a value onto the min_stack only when 
# it is less than or equal to the current minimum, we can retrieve the minimum in constant time. 
# Since every operation is O(1), it meets the design requirements perfectly.
class MinStack_optimal:
    def __init__(self):
        self.main_stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.main_stack.append(val)
        # Push to min_stack if it's empty or val is smaller/equal to current min
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        if not self.main_stack:
            return
        
        # If the value being popped is the current minimum, pop it from min_stack too
        val = self.main_stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.main_stack[-1] if self.main_stack else None

    def getMin(self) -> int:
        return self.min_stack[-1] if self.min_stack else None

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package stack;

import java.util.Stack;

public class MinStack {
    private Stack<Integer> mainStack;
    private Stack<Integer> minStack;

    public MinStack() {
        mainStack = new Stack<>();
        minStack = new Stack<>();
    }

    public void push(int val) {
        mainStack.push(val);
        if (minStack.isEmpty() || val <= minStack.peek()) {
            minStack.push(val);
        }
    }

    public void pop() {
        if (mainStack.isEmpty()) return;
        
        int removedValue = mainStack.pop();
        if (removedValue == minStack.peek()) {
            minStack.pop();
        }
    }

    public int top() {
        return mainStack.peek();
    }

    public int getMin() {
        return minStack.peek();
    }
}
"""
