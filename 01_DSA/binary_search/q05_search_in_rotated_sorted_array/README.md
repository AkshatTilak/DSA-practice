```markdown
### 🎯 Search In Rotated Sorted Array (q05_search_in_rotated_sorted_array)

#### 📝 Overview & Problem Explanation

The challenge asks us to find the index of a given `target` value within a `rotated sorted array`. A "rotated sorted array" is an array that was originally sorted in ascending order, but then some portion of it was moved from the end to the beginning. The array is rotated at an unknown pivot index. All elements in the array are unique.

**Example of a Rotated Sorted Array:**
Original: `[0, 1, 2, 4, 5, 6, 7]`
Rotated at pivot 3: `[4, 5, 6, 7, 0, 1, 2]` (elements `0,1,2` moved from start to end after rotation)

**Inputs:**
*   `nums`: A list of unique integers that was originally sorted in ascending order, but has been rotated at some unknown pivot.
*   `target`: An integer value we are searching for.

**Output:**
*   The index of `target` in `nums` if it exists.
*   `-1` if `target` is not found.

**Constraints (from LeetCode):**
*   `n == nums.length`
*   `1 <= n <= 5000`
*   `-10^4 <= nums[i] <= 10^4`
*   All values of `nums` are unique.
*   `nums` is an ascending sorted array that is potentially rotated at an unknown pivot index `k`.
*   `-10^4 <= target <= 10^4`

**Edge Cases to Consider:**
*   An array with only one element (e.g., `nums = [1], target = 0` -> `-1`, `nums = [1], target = 1` -> `0`).
*   The target element is the pivot element.
*   The array is not rotated at all (i.e., `k=0`).
*   The target is not present in the array.

#### 💡 Core Concepts & Algorithms

This problem is a classic application of a modified **Binary Search**.

**Why Binary Search?**
Even though the array is rotated, it still retains a "partially sorted" property. A standard binary search works by repeatedly dividing the search interval in half. It's efficient for sorted arrays because it can quickly eliminate half of the remaining elements.

**The Challenge with Rotation:**
The primary difficulty is that the `mid` element might not divide the array into two fully sorted halves. For example, in `[4, 5, 6, 7, 0, 1, 2]`, if `mid` points to `7`, the left part `[4, 5, 6, 7]` is sorted, but the right part `[0, 1, 2]` is also sorted, but `7 > 0`. A naive `target < nums[mid]` check would be misleading.

**Key Insight for Modified Binary Search:**
The crucial observation is that for any `mid` element, **at least one half of the array (either `[low...mid]` or `[mid...high]`) must be sorted**. We can use this property to strategically decide which half to continue our search in.

1.  **Identify the Sorted Half:** Compare `nums[low]` with `nums[mid]`.
    *   If `nums[low] <= nums[mid]`, the left half `[low...mid]` is sorted.
    *   If `nums[low] > nums[mid]`, then the right half `[mid...high]` must be sorted (and the pivot is in the left half).

2.  **Determine Search Direction:** Once the sorted half is identified, check if the `target` falls within the range of that sorted half.
    *   If `target` is within the sorted half's range, then continue binary search in that sorted half.
    *   If `target` is NOT within the sorted half's range, then it *must* be in the *other* (unsorted) half. Continue binary search in that unsorted half.

This approach guarantees that we eliminate half of the search space in each step, maintaining the `O(log N)` time complexity of binary search.

#### 🚀 Step-by-Step Logic & Solutions

---

**1. Naive / Brute Force Approach: Linear Scan**

*   **Logic:** The simplest approach is to iterate through the entire array from the beginning to the end. For each element, check if it matches the `target`. If a match is found, return its index. If the loop completes without finding the target, return `-1`.

*   **Step-by-Step:**
    1.  Initialize a loop counter `i` from `0` to `len(nums) - 1`.
    2.  In each iteration, check if `nums[i]` is equal to `target`.
    3.  If they are equal, return `i`.
    4.  If the loop finishes without returning, it means `target` was not found. Return `-1`.

*   **Dry Run Example:** `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0`
    *   `i = 0, nums[0] = 4` (not 0)
    *   `i = 1, nums[1] = 5` (not 0)
    *   `i = 2, nums[2] = 6` (not 0)
    *   `i = 3, nums[3] = 7` (not 0)
    *   `i = 4, nums[4] = 0` (equals target!) -> Return `4`.

*   **Code Sketch (for conceptual understanding):**
    ```python
    def search_rotated_brute_force(nums: list[int], target: int) -> int:
        for i in range(len(nums)):
            if nums[i] == target:
                return i
        return -1
    ```

---

**2. Optimal Approach: Modified Binary Search**

*   **Logic:** This approach leverages the "at least one half is sorted" property discussed above to efficiently narrow down the search space.

*   **Step-by-Step:**
    1.  Initialize two pointers: `low = 0` and `high = len(nums) - 1`.
    2.  Start a `while` loop that continues as long as `low <= high`.
    3.  Calculate the middle index: `mid = (low + high) // 2`.
    4.  **Check if `nums[mid]` is the target:**
        *   If `nums[mid] == target`, we found it! Return `mid`.
    5.  **Determine which half is sorted:**
        *   **Case A: Left half `[low...mid]` is sorted** (`nums[low] <= nums[mid]`).
            *   Check if `target` lies within this sorted left half: `nums[low] <= target < nums[mid]`.
                *   If yes, the target is in the left sorted half. Discard the right half by setting `high = mid - 1`.
                *   If no, the target must be in the unsorted right half. Discard the left half by setting `low = mid + 1`.
        *   **Case B: Right half `[mid...high]` is sorted** (`nums[low] > nums[mid]`).
            *   Check if `target` lies within this sorted right half: `nums[mid] < target <= nums[high]`.
                *   If yes, the target is in the right sorted half. Discard the left half by setting `low = mid + 1`.
                *   If no, the target must be in the unsorted left half. Discard the right half by setting `high = mid - 1`.
    6.  If the loop finishes (i.e., `low > high`), it means `target` was not found in the array. Return `-1`.

*   **Dry Run Example:** `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0`

    *   **Initial:** `low = 0`, `high = 6`
    *   **Iteration 1:**
        *   `mid = (0 + 6) // 2 = 3`. `nums[mid] = nums[3] = 7`.
        *   `target` (0) is not equal to `nums[mid]` (7).
        *   Check sorted half: `nums[low]` (4) vs `nums[mid]` (7). `4 <= 7` is **True**. Left half `[4, 5, 6, 7]` is sorted.
        *   Is `target` (0) in `[nums[low], nums[mid])` (i.e., `4 <= 0 < 7`)? **False**.
        *   Target is not in the sorted left half, so it must be in the unsorted right half.
        *   Update `low = mid + 1 = 4`.
        *   `low = 4`, `high = 6`

    *   **Iteration 2:**
        *   `mid = (4 + 6) // 2 = 5`. `nums[mid] = nums[5] = 1`.
        *   `target` (0) is not equal to `nums[mid]` (1).
        *   Check sorted half: `nums[low]` (0) vs `nums[mid]` (1). `0 <= 1` is **True**. Left half `[0, 1]` is sorted.
        *   Is `target` (0) in `[nums[low], nums[mid])` (i.e., `0 <= 0 < 1`)? **True**.
        *   Target is in the sorted left half.
        *   Update `high = mid - 1 = 4`.
        *   `low = 4`, `high = 4`

    *   **Iteration 3:**
        *   `mid = (4 + 4) // 2 = 4`. `nums[mid] = nums[4] = 0`.
        *   `target` (0) is equal to `nums[mid]` (0). **Found!**
        *   Return `mid = 4`.

*   **Python Implementation:**

    ```python
    def search_rotated(nums: list[int], target: int) -> int:
        low, high = 0, len(nums) - 1

        while low <= high:
            mid = (low + high) // 2

            if nums[mid] == target:
                return mid

            # Check if the left half is sorted
            if nums[low] <= nums[mid]:
                # Target is in the left sorted half
                if nums[low] <= target < nums[mid]:
                    high = mid - 1
                # Target is in the right unsorted half
                else:
                    low = mid + 1
            # The right half must be sorted
            else:
                # Target is in the right sorted half
                if nums[mid] < target <= nums[high]:
                    low = mid + 1
                # Target is in the left unsorted half
                else:
                    high = mid - 1
        
        # Target not found
        return -1

    ```

#### 📊 Complexity Analysis

| Approach                | Time Complexity | Space Complexity |
| :---------------------- | :-------------- | :--------------- |
| Brute Force (Linear Scan) | O(N)            | O(1)             |
| Optimal (Binary Search) | O(log N)        | O(1)             |

*   **Brute Force (Linear Scan):**
    *   **Time Complexity:** `O(N)` because, in the worst case, we might have to iterate through all `N` elements of the array to find the target or determine it's not present.
    *   **Space Complexity:** `O(1)` as it only uses a few constant extra variables (e.g., a loop counter).

*   **Optimal (Binary Search):**
    *   **Time Complexity:** `O(log N)` because each step of the binary search effectively halves the search space. For an array of `N` elements, it takes approximately `log2(N)` steps to narrow down the search to a single element.
    *   **Space Complexity:** `O(1)` as it only uses a few constant extra variables (`low`, `high`, `mid`).

#### 🌐 Real-World Applications

The "Search in Rotated Sorted Array" problem and its underlying modified binary search pattern have several real-world applications in scenarios where data is ordered but might have structural shifts or circularity:

1.  **Distributed Database Indexing / Sharding:** Imagine a large database index that is sharded across multiple servers. If these shards are conceptually sorted but accessed in a "rotated" fashion (e.g., due to load balancing, fault tolerance, or consistent hashing), a modified binary search could be used to quickly locate the correct shard or data block for a given key.

2.  **Circular Buffers and Log Files:** Data structures like circular buffers (used in networking, audio processing, logging) maintain a fixed-size queue where the "end" wraps around to the "beginning." If elements within this buffer are sorted by timestamp or some ID, searching for a specific item might involve traversing a logically "rotated" sorted sequence. Similarly, searching through wrapped-around log files by timestamp could use a similar technique.

3.  **Network Routing Tables:** In complex network topologies, routing tables might be optimized or reconfigured dynamically. If IP ranges or next-hop pointers are stored in a conceptually sorted list that undergoes "rotation" or reordering, this algorithm could help in efficiently finding the next hop for a given destination IP.

4.  **Hardware Controllers and Sensor Data:** Systems that manage sequences of events or sensor readings (e.g., in industrial control, automotive systems) often store this data in efficient, perhaps circular, memory structures. If these sequences are sorted by time or event ID, a search for a particular event could leverage the principles of searching in a rotated sorted array.

5.  **Compiler Optimization / Symbol Tables:** In certain compiler optimizations or symbol table lookups, where symbols or memory addresses are managed in an ordered fashion but might be subject to dynamic remapping or re-segmentation, this pattern could arise.