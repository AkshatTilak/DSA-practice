"""
Challenge: q05_top_k_frequent_elements
Difficulty: Medium
Link: https://leetcode.com/problems/top-k-frequent-elements/

Problem:
Return the k most frequent elements.
"""

# --- STARTER TEMPLATE FOR USER ---
def top_k_frequent(nums: list[int], k: int) -> list[int]:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N log N)
# Space Complexity: O(N)
# This approach uses a hash map to count frequencies and then sorts the unique elements 
# based on their frequency in descending order. The time complexity is dominated 
# by the sorting step.
def top_k_frequent_naive(nums: list[int], k: int) -> list[int]:
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    
    # Sort unique elements by frequency value in descending order
    sorted_elements = sorted(counts.keys(), key=lambda x: counts[x], reverse=True)
    
    return sorted_elements[:k]

# --- APPROACH 2: Optimal (Bucket Sort) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This approach uses Bucket Sort. Instead of sorting by frequency, we create an array 
# where the index represents the frequency of elements. Since the maximum frequency 
# is the length of the input array N, we can map frequencies to indices in O(N) time.
# This is optimal as it avoids the O(N log N) or O(N log k) overhead of sorting or heaps.
def top_k_frequent_optimal(nums: list[int], k: int) -> list[int]:
    count_map = {}
    for num in nums:
        count_map[num] = count_map.get(num, 0) + 1
        
    # Create buckets where index is frequency and value is list of elements with that frequency
    # freq[i] contains all numbers that appear exactly i times
    freq = [[] for _ in range(len(nums) + 1)]
    for num, count in count_map.items():
        freq[count].append(num)
        
    result = []
    # Iterate through buckets from highest frequency to lowest
    for i in range(len(freq) - 1, 0, -1):
        for num in freq[i]:
            result.append(num)
            if len(result) == k:
                return result
    
    return result

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package arrays_and_hashing;

import java.util.*;

public class TopKFrequentElements {
    /**
     * Implementation using Bucket Sort to achieve linear time complexity.
     * Time Complexity: O(N)
     * Space Complexity: O(N)
     */
    public int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> countMap = new HashMap<>();
        for (int num : nums) {
            countMap.put(num, countMap.getOrDefault(num, 0) + 1);
        }

        // Bucket array: indices are frequencies, values are lists of numbers
        List<Integer>[] bucket = new List[nums.length + 1];
        for (int key : countMap.keySet()) {
            int frequency = countMap.get(key);
            if (bucket[frequency] == null) {
                bucket[frequency] = new ArrayList<>();
            }
            bucket[frequency].add(key);
        }

        int[] result = new int[k];
        int index = 0;
        // Iterate backwards from the highest possible frequency
        for (int i = bucket.length - 1; i >= 0 && index < k; i--) {
            if (bucket[i] != null) {
                for (int num : bucket[i]) {
                    result[index++] = num;
                    if (index == k) {
                        return result;
                    }
                }
            }
        }
        return result;
    }

    public static void main(String[] args) {
        TopKFrequentElements solver = new TopKFrequentElements();
        int[] nums = {1, 1, 1, 2, 2, 3};
        int k = 2;
        System.out.println(Arrays.toString(solver.topKFrequent(nums, k))); // Output: [1, 2]
    }
}
"""
