"""
Challenge: q07_course_schedule
Difficulty: Medium
Link: https://leetcode.com/problems/course-schedule/

Problem:
Topological sort course check.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (DFS Cycle Detection) ---
# Time Complexity: O(V + E)
# Space Complexity: O(V + E)
# This approach uses Depth First Search (DFS) to detect cycles in the directed graph. 
# We maintain a 'visited' set to avoid redundant work and a 'path' set (recursion stack) 
# to detect if we encounter a node that is already part of the current traversal path, 
# which indicates a cycle.
def canFinish_naive(numCourses: int, prerequisites: list[list[int]]) -> bool:
    adj = [[] for _ in range(numCourses)]
    for course, pre in prerequisites:
        adj[pre].append(course)
    
    visited = [False] * numCourses
    path = [False] * numCourses
    
    def has_cycle(u):
        visited[u] = True
        path[u] = True
        
        for v in adj[u]:
            if not visited[v]:
                if has_cycle(v):
                    return True
            elif path[v]:
                return True
        
        path[u] = False
        return False

    for i in range(numCourses):
        if not visited[i]:
            if has_cycle(i):
                return False
    return True

# --- APPROACH 2: Optimal (Kahn's Algorithm - BFS Topological Sort) ---
# Time Complexity: O(V + E)
# Space Complexity: O(V + E)
# Kahn's Algorithm is the optimal approach for this problem because it iteratively 
# processes nodes with an in-degree of 0. It avoids the risk of StackOverflowError 
# associated with deep recursion in DFS and directly simulates the process of 
# taking courses as their prerequisites are completed. If the number of processed 
# nodes equals the total number of courses, the graph is a Directed Acyclic Graph (DAG).
from collections import deque

def canFinish_optimal(numCourses: int, prerequisites: list[list[int]]) -> bool:
    # Step 1: Build adjacency list and calculate in-degrees
    adj = [[] for _ in range(numCourses)]
    in_degree = [0] * numCourses
    
    for course, pre in prerequisites:
        adj[pre].append(course)
        in_degree[course] += 1
        
    # Step 2: Initialize queue with all courses having no prerequisites
    queue = deque([i for i in range(numCourses) if in_degree[i] == 0])
    
    courses_taken = 0
    
    # Step 3: Process the queue
    while queue:
        u = queue.popleft()
        courses_taken += 1
        
        for v in adj[u]:
            in_degree[v] -= 1
            # If in-degree becomes 0, all prerequisites for course v are met
            if in_degree[v] == 0:
                queue.append(v)
                
    # If we processed all courses, no cycle exists
    return courses_taken == numCourses

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package graphs;

import java.util.*;

public class CourseSchedule {
    /**
     * Determines if all courses can be finished given the prerequisites.
     * This implementation uses Kahn's Algorithm (BFS Topological Sort).
     */
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        if (numCourses <= 0) return true;
        
        List<List<Integer>> adj = new ArrayList<>();
        int[] inDegree = new int[numCourses];
        
        for (int i = 0; i < numCourses; i++) {
            adj.add(new ArrayList<>());
        }
        
        // Build the graph
        for (int[] pair : prerequisites) {
            int course = pair[0];
            int pre = pair[1];
            adj.get(pre).add(course);
            inDegree[course]++;
        }
        
        // Queue for courses with no prerequisites
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < numCourses; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }
        
        int count = 0;
        while (!queue.isEmpty()) {
            int current = queue.poll();
            count++;
            
            for (int neighbor : adj.get(current)) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] == 0) {
                    queue.offer(neighbor);
                }
            }
        }
        
        // If count equals numCourses, then it's a DAG
        return count == numCourses;
    }

    public static void main(String[] args) {
        CourseSchedule solver = new CourseSchedule();
        int[][] pre1 = {{1, 0}};
        System.out.println(solver.canFinish(2, pre1)); // True
        
        int[][] pre2 = {{1, 0}, {0, 1}};
        System.out.println(solver.canFinish(2, pre2)); // False
    }
}
"""
