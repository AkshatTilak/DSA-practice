"""
Challenge: q02_last_stone_weight
Difficulty: Easy
Link: https://leetcode.com/problems/last-stone-weight/

Problem:
Last stone weight using max heap.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(n^2 log n)
# Space Complexity: O(1) or O(n) depending on the sorting implementation
# This approach sorts the list of stones in every iteration to find the two heaviest stones.
# After smashing them and inserting the remainder, it re-sorts the list.
def solve_naive(stones):
    stones = list(stones)
    while len(stones) > 1:
        stones.sort()
        # Extract the two largest stones
        s1 = stones.pop()
        s2 = stones.pop()
        
        if s1 != s2:
            # Push the difference back into the list
            stones.append(abs(s1 - s2))
            
    return stones[0] if stones else 0

# --- APPROACH 2: Optimal (Max Heap) ---
# Time Complexity: O(n log n)
# Space Complexity: O(n)
# This approach uses a Max Heap to efficiently retrieve and remove the two heaviest stones.
# In Python, heapq is a min-heap, so we multiply all stone weights by -1 to simulate a max-heap.
# Heapification takes O(n), and each of the (n-1) smash operations takes O(log n).
import heapq

def solve_optimal(stones):
    # Convert stones to negative to use heapq as a max heap
    max_heap = [-s for s in stones]
    heapq.heapify(max_heap)
    
    while len(max_heap) > 1:
        # Pop the two heaviest stones (most negative)
        first = -heapq.heappop(max_heap)
        second = -heapq.heappop(max_heap)
        
        if first != second:
            # Push the difference back as a negative value
            heapq.heappush(max_heap, -(first - second))
            
    # The remaining stone is the absolute value of the last element, or 0 if empty
    return -max_heap[0] if max_heap else 0

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package heap;

import java.util.PriorityQueue;
import java.util.Collections;

public class LastStoneWeight {
    /**
     * Solves the Last Stone Weight problem using a PriorityQueue (Max Heap).
     * Time Complexity: O(n log n)
     * Space Complexity: O(n)
     */
    public int lastStoneWeight(int[] stones) {
        if (stones == null || stones.length == 0) {
            return 0;
        }

        // Max heap using Collections.reverseOrder()
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());
        for (int stone : stones) {
            maxHeap.offer(stone);
        }

        while (maxHeap.size() > 1) {
            int stone1 = maxHeap.poll();
            int stone2 = maxHeap.poll();

            if (stone1 != stone2) {
                maxHeap.offer(stone1 - stone2);
            }
        }

        return maxHeap.isEmpty() ? 0 : maxHeap.poll();
    }

    public static void main(String[] args) {
        LastStoneWeight solver = new LastStoneWeight();
        int[] stones = {2, 7, 4, 1, 8, 1};
        System.out.println("Last stone weight: " + solver.lastStoneWeight(stones)); // Output: 1
    }
}
"""
