INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/top-k-frequent-elements/',
    'description': 'Return the k most frequent elements.',
    'groups': ['Array', 'Hashing', 'Heap / Priority Queue'],
    'starter_code': """def top_k_frequent(nums: list[int], k: int) -> list[int]:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
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
\"\"\"
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
\"\"\"""",
    'test_code': """def test_top_k():
    assert set(top_k_frequent([1,1,1,2,2,3], 2)) == {1, 2}""",
    'readme_content': """# Top K Frequent Elements (q05_top_k_frequent_elements)

## Overview & Problem Explanation

The "Top K Frequent Elements" challenge requires you to identify and return the `k` elements that appear most frequently in a given integer array. The order in which you return these `k` elements does not matter.

Imagine you have a list of numbers like `[1, 1, 1, 2, 2, 3]` and you need to find the `2` most frequent elements.
*   `1` appears 3 times.
*   `2` appears 2 times.
*   `3` appears 1 time.
The two most frequent elements are `1` and `2`.

**Inputs:**
*   `nums`: A list of integers (e.g., `[1,1,1,2,2,3]`).
*   `k`: An integer representing the number of most frequent elements to return (e.g., `2`).

**Outputs:**
*   A list of `k` integers, representing the elements with the highest frequencies.

**Constraints:**
*   The length of the `nums` array will be between 1 and 10⁵ (i.e., `1 <= nums.length <= 10^5`).
*   The values of `nums[i]` will be between -10⁴ and 10⁴ (i.e., `-10^4 <= nums[i] <= 10^4`).
*   `k` will be in the range `[1, number of unique elements]` in the array, meaning `k` is always valid.
*   The answer is guaranteed to be unique, meaning there will be no ties for the k-th frequent element that would lead to ambiguity.
*   Your algorithm's time complexity must be better than `O(N log N)`, where `N` is the array's size.

**Edge Cases to Consider:**
*   `k` equals the number of unique elements: All unique elements should be returned.
*   All elements are unique: In this case, any `k` elements can be considered the "top k frequent" if `k` is less than the total unique elements. However, the problem statement guarantees a unique answer.
*   All elements are the same: The single unique element will be the most frequent.
*   An array with a single element: This element will be the most frequent.

## Core Concepts & Data Structures/Algorithms

Solving this problem efficiently hinges on two key stages:
1.  **Counting Frequencies**: Determining how many times each unique number appears.
2.  **Selecting Top K**: Efficiently finding the `k` elements with the highest counts.

The problem specifically asks for a solution better than `O(N log N)`. This usually points away from general-purpose sorting of all elements and towards more specialized data structures.

### 1. Hash Maps (Dictionaries)
*   **Why chosen**: Hash maps (or dictionaries in Python, `HashMap` in Java) are ideal for frequency counting because they provide `O(1)` average time complexity for insertions, deletions, and lookups. This allows us to iterate through the input array once and build a complete frequency count for all unique elements.
*   **How it works**: Each unique number from the `nums` array serves as a key, and its corresponding value stores the count of its occurrences.

### 2. Heaps (Priority Queues)
*   **Why chosen**: When you need to find the "top K" or "K largest/smallest" elements without fully sorting the entire dataset, a heap (specifically a min-heap for finding the *largest* K elements) is a highly efficient data structure. It allows you to maintain a collection of `k` elements such that you can always access the smallest/largest among them in `O(1)` time, and add/remove elements in `O(log K)` time.
*   **How it works (for this problem)**: We use a **min-heap** of size `k`. We store pairs of `(frequency, number)` in the heap.
    *   As we process each `(number, frequency)` pair from our frequency map:
        *   We push the `(frequency, number)` into the min-heap.
        *   If the heap size exceeds `k`, we `pop` the smallest element (which will be the element with the lowest frequency among the `k` elements currently in the heap) to ensure only the top `k` most frequent elements are retained.
    *   This strategy ensures that by the end, the heap contains the `k` elements with the highest frequencies.

### 3. Bucket Sort (Frequency Array / List of Lists)
*   **Why chosen**: This approach leverages the constraint that frequencies are bounded by the input array's length (`N`). Since an element can appear at most `N` times, we can create an array of "buckets" where each index represents a frequency, and the value at that index is a list of numbers that appear with that exact frequency. This allows for `O(N)` time complexity.
*   **How it works**:
    *   First, count frequencies using a hash map (same as above).
    *   Create a list of lists (or an array of lists) called `buckets` of size `N + 1`. `buckets[i]` will store all numbers that appear `i` times.
    *   Iterate through the frequency map. For each `(number, frequency)` pair, append `number` to `buckets[frequency]`.
    *   Finally, iterate through the `buckets` array from the highest possible frequency (index `N`) down to `1`. Collect numbers from these buckets until `k` elements have been gathered. Since we are iterating from highest frequency down, the first `k` elements collected will be the most frequent.

## Step-by-Step Logic

Let's walk through the logic for different approaches using `nums = [1, 1, 1, 2, 2, 3]`, `k = 2`.

### Approach 1: Hash Map + Sorting (Naive/Brute-Force)

This is a straightforward approach but typically exceeds the `O(N log N)` time complexity requirement for larger inputs if not optimized.

1.  **Count Frequencies**: Use a hash map to store the frequency of each number.
    *   `freq_map = {1: 3, 2: 2, 3: 1}`
2.  **Convert to List of Pairs**: Transform the hash map into a list of `(number, frequency)` tuples.
    *   `[(1, 3), (2, 2), (3, 1)]`
3.  **Sort by Frequency**: Sort this list in descending order based on frequency.
    *   `sorted_elements = [(1, 3), (2, 2), (3, 1)]`
4.  **Extract Top K**: Take the first `k` elements from the sorted list and return their numbers.
    *   For `k = 2`, we take `(1, 3)` and `(2, 2)`.
    *   Result: `[1, 2]`

### Approach 2: Hash Map + Min-Heap (Optimal O(N log K))

This approach is generally preferred when `k` is significantly smaller than `N`.

1.  **Count Frequencies**: Use a hash map to store the frequency of each number.
    *   `freq_map = {1: 3, 2: 2, 3: 1}`
2.  **Initialize Min-Heap**: Create an empty min-heap (Python's `heapq` module provides min-heap functionality). The heap will store `(frequency, number)` tuples.
    *   `min_heap = []`
3.  **Populate Heap**: Iterate through the `freq_map`. For each `(number, frequency)` pair:
    *   Push `(frequency, number)` into the `min_heap`.
    *   If the size of the `min_heap` exceeds `k`, `pop` the smallest element (which corresponds to the lowest frequency currently in the heap).
    *   **Iteration 1: (1, 3)**
        *   Push `(3, 1)`: `min_heap = [(3, 1)]`
    *   **Iteration 2: (2, 2)**
        *   Push `(2, 2)`: `min_heap = [(2, 2), (3, 1)]` (heap property maintained, `(2,2)` is root)
        *   Heap size is `2`, which equals `k`. No pop.
    *   **Iteration 3: (3, 1)**
        *   Push `(1, 3)`: `min_heap = [(1, 3), (3, 1), (2, 2)]` (after heapify)
        *   Heap size is `3`, which is greater than `k = 2`.
        *   Pop the smallest element: `(1, 3)` is popped.
        *   `min_heap = [(2, 2), (3, 1)]`
4.  **Extract Results**: After processing all elements, the `min_heap` contains `k` elements, which are the `k` most frequent. Extract the numbers from these tuples.
    *   `result = []`
    *   Pop `(2, 2)`: `result.append(2)` -> `[2]`
    *   Pop `(3, 1)`: `result.append(1)` -> `[2, 1]` (Order doesn't matter, so `[1, 2]` is also valid).
    *   Result: `[2, 1]` (or `[1, 2]`)

### Approach 3: Hash Map + Bucket Sort (Optimal O(N))

This is the most efficient approach in terms of theoretical time complexity.

1.  **Count Frequencies**: Use a hash map to store the frequency of each number.
    *   `freq_map = {1: 3, 2: 2, 3: 1}`
2.  **Initialize Buckets**: Create a list of lists (buckets) where the index represents the frequency, and the inner list stores numbers with that frequency. The size of the `buckets` list should be `N + 1` (where `N` is `len(nums)`), as the maximum possible frequency is `N`.
    *   `N = len(nums) = 6`
    *   `buckets = [[] for _ in range(N + 1)]` (i.e., `[[], [], [], [], [], [], []]`)
3.  **Populate Buckets**: Iterate through the `freq_map`. For each `(number, frequency)` pair, append the `number` to `buckets[frequency]`.
    *   For `(1, 3)`: `buckets[3].append(1)` -> `buckets = [[], [], [], [1], [], [], []]`
    *   For `(2, 2)`: `buckets[2].append(2)` -> `buckets = [[], [], [2], [1], [], [], []]`
    *   For `(3, 1)`: `buckets[1].append(3)` -> `buckets = [[], [3], [2], [1], [], [], []]`
4.  **Collect Top K**: Iterate `buckets` from the highest frequency index down to `1`. Collect elements until `k` elements are found.
    *   `result = []`
    *   Loop `i` from `N` down to `1` (i.e., `6, 5, 4, 3, 2, 1`):
        *   `i = 6`: `buckets[6]` is `[]`.
        *   `i = 5`: `buckets[5]` is `[]`.
        *   `i = 4`: `buckets[4]` is `[]`.
        *   `i = 3`: `buckets[3]` is `[1]`.
            *   For `num = 1` in `buckets[3]`:
                *   `result.append(1)` -> `[1]`
                *   `len(result)` is `1`. We need `k = 2`.
        *   `i = 2`: `buckets[2]` is `[2]`.
            *   For `num = 2` in `buckets[2]`:
                *   `result.append(2)` -> `[1, 2]`
                *   `len(result)` is `2`. We have `k` elements. Break.
    *   Result: `[1, 2]`

## Complexity Analysis

Here's a summary of the time and space complexity for each approach:

| Approach                    | Time Complexity | Space Complexity | Reasoning                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :-------------------------- | :-------------- | :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Hash Map + Sorting**   | `O(N log M)`    | `O(M)`           | **Time**: `O(N)` to count frequencies into the hash map (where `M` is the number of unique elements). `O(M log M)` to sort the `M` unique elements by frequency. In the worst case, `M = N`, so `O(N log N)`. **Space**: `O(M)` for the frequency map.                                                                                                                                                                                                  |
| **2. Hash Map + Min-Heap**  | `O(N log K)`    | `O(N + K)`       | **Time**: `O(N)` to count frequencies. `O(N log K)` for heap operations: `N` elements are processed, each insertion/deletion takes `O(log K)` as the heap size is capped at `K`. **Space**: `O(N)` for the frequency map (stores up to `N` unique elements) and `O(K)` for the heap (stores `K` elements). So, `O(N + K)` which simplifies to `O(N)` in the worst case (when `K` is close to `N`). |
| **3. Hash Map + Bucket Sort** | `O(N)`          | `O(N)`           | **Time**: `O(N)` to count frequencies. `O(N)` to populate the buckets (iterate through `M` unique elements, each append is `O(1)`). `O(N)` to iterate through buckets (at most `N` buckets) and collect `k` elements. Overall `O(N)`. **Space**: `O(N)` for the frequency map. `O(N)` for the `buckets` array (which contains all `N` numbers distributed across buckets). Overall `O(N)`.                                                       |

*(Note: `N` is the number of elements in `nums`, `M` is the number of unique elements.)*

## Real-World Applications

The "Top K Frequent Elements" pattern is surprisingly common in various software systems, especially when dealing with data analysis, recommendations, or performance monitoring:

1.  **Trending Topics/Hashtags**: Social media platforms like Twitter use this to identify the top `k` trending hashtags or topics globally or within a specific region.
2.  **Recommendation Systems**: E-commerce sites (e.g., Amazon) or streaming services (e.g., Netflix) might use this to find the "top `k` most purchased items," "most watched movies," or "frequently searched products" to recommend to users.
3.  **Log Analysis and Error Reporting**: In system monitoring, identifying the top `k` most frequent error messages or log events helps engineers quickly pinpoint critical issues in a system.
4.  **Search Autocomplete/Query Suggestions**: Search engines use the frequency of past queries to suggest the most common completions as a user types, improving search efficiency.
5.  **Network Traffic Analysis**: Detecting the top `k` most frequent IP addresses communicating with a server can help identify potential attacks or high-demand services.
6.  **Compiler Parsing**: During lexical analysis or intermediate code generation, identifying frequently used tokens or sub-expressions might inform optimization strategies.""",
}
