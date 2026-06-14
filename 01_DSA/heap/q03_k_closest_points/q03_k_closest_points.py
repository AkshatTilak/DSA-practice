"""
Challenge: q03_k_closest_points
Difficulty: Medium
Link: https://leetcode.com/problems/k-closest-points-to-origin/

Problem:
Find K closest points.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N log N)
# Space Complexity: O(N)
# This approach calculates the distance for all points, sorts the entire list based on these distances, and returns the first K elements.
def solve_naive(points: list[list[int]], k: int) -> list[list[int]]:
    def get_dist(point):
        return point[0]**2 + point[1]**2
    
    # Sort points based on distance from origin
    points.sort(key=get_dist)
    return points[:k]

# --- APPROACH 2: Optimal (Max-Heap) ---
# Time Complexity: O(N log K)
# Space Complexity: O(K)
# This approach maintains a max-heap of size K. For every point, we calculate the distance and push it into the heap. 
# If the heap exceeds size K, we pop the point with the maximum distance. 
# This ensures the heap always contains the K closest points encountered so far. 
# It is optimal because it reduces the time complexity from O(N log N) to O(N log K), which is significantly 
# faster when K is much smaller than N.
import heapq

def solve_optimal(points: list[list[int]], k: int) -> list[list[int]]:
    # We use a max-heap to keep track of the k smallest distances.
    # Python's heapq is a min-heap, so we store distances as negative values.
    max_heap = []
    
    for x, y in points:
        dist = -(x**2 + y**2)
        if len(max_heap) < k:
            heapq.heappush(max_heap, (dist, [x, y]))
        else:
            # If the current point is closer than the farthest point in our heap, replace it.
            # Since dist is negative, a larger 'dist' value means a smaller actual distance.
            if dist > max_heap[0][0]:
                heapq.heapreplace(max_heap, (dist, [x, y]))
                
    return [point for dist, point in max_heap]

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package heap;

import java.util.*;

public class KClosestPoints {
    /**
     * Finds the K closest points to the origin (0,0).
     * Time Complexity: O(N log K)
     * Space Complexity: O(K)
     */
    public int[][] kClosest(int[][] points, int k) {
        // Use a PriorityQueue as a Max-Heap.
        // Compare distance (x^2 + y^2) in descending order.
        PriorityQueue<int[]> maxHeap = new PriorityQueue<>((a, b) -> 
            Integer.compare((b[0] * b[0] + b[1] * b[1]), (a[0] * a[0] + a[1] * a[1]))
        );
        
        for (int[] point : points) {
            maxHeap.offer(point);
            if (maxHeap.size() > k) {
                maxHeap.poll();
            }
        }
        
        int[][] result = new int[k][2];
        int i = 0;
        while (!maxHeap.isEmpty()) {
            result[i++] = maxHeap.poll();
        }
        return result;
    }

    public static void main(String[] args) {
        KClosestPoints solver = new KClosestPoints();
        int[][] points = {{1, 3}, {-2, 2}};
        int k = 1;
        int[][] result = solver.kClosest(points, k);
        System.out.println(Arrays.deepToString(result)); // Expected: [[-2, 2]]
    }
}
"""
