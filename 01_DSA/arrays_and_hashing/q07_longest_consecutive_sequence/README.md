# Longest Consecutive Sequence

### Overview & Problem Explanation

The "Longest Consecutive Sequence" challenge asks us to find the length of the longest sequence of consecutive integers within an unsorted array of integers. The key here is that the numbers forming the consecutive sequence do not need to be contiguous in the original input array; their numerical values just need to form a consecutive series (e.g., 1, 2, 3, 4). The problem explicitly requires an algorithm that runs in **O(N)** time complexity.

**Example:**

*   **Input**: `nums = [100, 4, 200, 1, 3, 2]`
*   **Output**: `4`
*   **Explanation**: The longest consecutive elements sequence is `[1, 2, 3, 4]`, which has a length of 4.

**Inputs**:
*   `nums`: A list of integers.

**Outputs**:
*   An integer representing the length of the longest consecutive elements sequence.

**Constraints**:
*   `0 <= nums.length <= 10^5`
*   `-10^9 <= nums[i] <= 10^9`
*   The solution must run in `O(N)` time complexity.

**Edge Cases**:
*   **Empty input array**: If `nums` is empty, the longest consecutive sequence length is `0`.
*   **Array with one element**: The longest consecutive sequence length is `1`.
*   **All same elements**: e.g., `[5, 5, 5]`. The length would be `1`.
*   **Duplicate elements**: Duplicates should not extend a sequence. For example, `[1, 2, 2, 3]` still has a longest consecutive sequence of `[1, 2, 3]` with length `3`. The use of a `HashSet` naturally handles duplicates.
*   **Negative numbers**: Consecutive sequences can include negative numbers (e.g., `[-2, -1, 0, 1]`).

### Core Concepts & Data Structures/Algorithms

The primary data structure for solving this problem efficiently in O(N) time is a **Hash Set (or `set` in Python)**.

**Why a Hash Set?**
1.  **O(1) Average Time Complexity for Lookups**: A hash set allows us to check for the presence of an element (using the `in` operator) in average constant time, `O(1)`. This is crucial for determining if `num - 1` or `num + 1` exists quickly, which is fundamental to building consecutive sequences.
2.  **Duplicate Handling**: When converting a list to a hash set, duplicate elements are automatically removed. This ensures that each unique number is considered exactly once, which is important for correct sequence counting and avoiding redundant work.

**The "Sequence Start" Optimization**:
A naive approach might involve iterating through each number and, for each number, trying to build a consecutive sequence both upwards and downwards. This can lead to redundant computations and an `O(N^2)` time complexity in the worst case.

The core optimization with a hash set is to **only attempt to build a sequence if the current number `num` is a *potential start* of a new consecutive sequence**. We determine this by checking if `num - 1` **does not exist** in our hash set.
*   If `num - 1` *does* exist, it means `num` is part of an already longer sequence that started at `num - 1` (or even earlier). In this case, we can skip `num` because we will eventually process the actual start of that sequence.
*   If `num - 1` *does not* exist, then `num` is indeed the smallest element in its consecutive sequence, making it a valid starting point for a new sequence check.

This optimization ensures that each number in the input array is part of a sequence length calculation at most once (when it's part of a `current_num + 1` check), leading to an overall `O(N)` time complexity.

### Step-by-Step Logic

Let's explore both a brute-force approach and the optimal hash set approach.

#### 1. Naive/Brute Force Approach (Sorting)

A straightforward idea is to sort the array first. Once sorted, checking for consecutive elements becomes trivial as they will be adjacent.

**Steps**:
1.  Sort the input `nums` array.
2.  Initialize `longest_sequence = 0` and `current_sequence = 0`.
3.  Iterate through the sorted array:
    *   If the current number is the same as the previous one, it's a duplicate; skip it.
    *   If the current number is `previous_number + 1`, increment `current_sequence`.
    *   Otherwise (not consecutive, not a duplicate), reset `current_sequence` to `1`.
    *   Update `longest_sequence = max(longest_sequence, current_sequence)`.
4.  Return `longest_sequence`.

**Why this isn't optimal**:
Sorting an array typically takes `O(N log N)` time complexity, which violates the `O(N)` requirement of the problem.

#### 2. Optimal Approach (Hash Set with Sequence Start Optimization)

This method leverages the `O(1)` average time lookup capability of hash sets to achieve the required `O(N)` time complexity.

**Steps**:
1.  **Handle Empty Input**: If `nums` is empty, return `0`.
2.  **Populate Hash Set**: Create a hash set, let's call it `num_set`, and insert all unique numbers from the input `nums` array into it. This takes `O(N)` time.
3.  **Initialize `longest_sequence`**: Set `longest_sequence = 0`.
4.  **Iterate and Check Sequence Starts**: Iterate through each `num` in the original `nums` array (or equivalently, iterate through the `num_set` itself). For each `num`:
    *   **Check for Sequence Start**: Determine if `num` is the potential start of a consecutive sequence. Do this by checking if `(num - 1)` **is NOT** present in `num_set`.
    *   **If it's a Sequence Start**:
        *   Initialize `current_num = num`.
        *   Initialize `current_sequence = 1`.
        *   **Extend the Sequence**: While `(current_num + 1)` **IS** present in `num_set`:
            *   Increment `current_num`.
            *   Increment `current_sequence`.
        *   **Update Longest**: After the inner `while` loop finishes (meaning the sequence has ended), update `longest_sequence = max(longest_sequence, current_sequence)`.
5.  **Return Result**: After iterating through all numbers, return `longest_sequence`.

**Dry Run Example**: `nums = [100, 4, 200, 1, 3, 2]`

1.  `nums` is not empty.
2.  `num_set = {100, 4, 200, 1, 3, 2}` (order in set doesn't matter for logic).
3.  `longest_sequence = 0`.

4.  **Iterate through `num` in `nums`**:

    *   **`num = 100`**:
        *   Is `(100 - 1) = 99` in `num_set`? No. So, `100` is a sequence start.
        *   `current_num = 100`, `current_sequence = 1`.
        *   Is `(100 + 1) = 101` in `num_set`? No. Inner loop ends.
        *   `longest_sequence = max(0, 1) = 1`.

    *   **`num = 4`**:
        *   Is `(4 - 1) = 3` in `num_set`? Yes. `4` is NOT a sequence start. Skip.

    *   **`num = 200`**:
        *   Is `(200 - 1) = 199` in `num_set`? No. So, `200` is a sequence start.
        *   `current_num = 200`, `current_sequence = 1`.
        *   Is `(200 + 1) = 201` in `num_set`? No. Inner loop ends.
        *   `longest_sequence = max(1, 1) = 1`.

    *   **`num = 1`**:
        *   Is `(1 - 1) = 0` in `num_set`? No. So, `1` is a sequence start.
        *   `current_num = 1`, `current_sequence = 1`.
        *   Is `(1 + 1) = 2` in `num_set`? Yes.
            *   `current_num = 2`, `current_sequence = 2`.
        *   Is `(2 + 1) = 3` in `num_set`? Yes.
            *   `current_num = 3`, `current_sequence = 3`.
        *   Is `(3 + 1) = 4` in `num_set`? Yes.
            *   `current_num = 4`, `current_sequence = 4`.
        *   Is `(4 + 1) = 5` in `num_set`? No. Inner loop ends.
        *   `longest_sequence = max(1, 4) = 4`.

    *   **`num = 3`**:
        *   Is `(3 - 1) = 2` in `num_set`? Yes. `3` is NOT a sequence start. Skip.

    *   **`num = 2`**:
        *   Is `(2 - 1) = 1` in `num_set`? Yes. `2` is NOT a sequence start. Skip.

5.  All numbers processed. Return `longest_sequence = 4`.

### Complexity Analysis

Here's a summary of the time and space complexity for the discussed approaches:

| Approach                          | Time Complexity | Space Complexity |
| :-------------------------------- | :-------------- | :--------------- |
| **Naive (Sorting)**               | O(N log N)      | O(1) or O(N)     |
| **Optimal (Hash Set)**            | O(N)            | O(N)             |

**Reasoning for Optimal (Hash Set)**:

*   **Time Complexity: O(N)**
    1.  **Populating the Hash Set**: Converting the `nums` list into a `num_set` takes `O(N)` time on average, as each of the `N` elements is inserted.
    2.  **Iterating and Building Sequences**: We iterate through each `num` in the input array. The crucial part is the "sequence start" optimization:
        *   Each number `num` is checked once with `(num - 1) in num_set`. This is an `O(1)` average time operation.
        *   If `num` is a sequence start, the inner `while` loop then traverses the consecutive elements (`current_num + 1`).
        *   Although there are nested loops, each number in `num_set` is visited at most a constant number of times across the entire algorithm:
            *   Once when it's initially added to the `num_set`.
            *   Once when it's checked if it's a sequence start (`num - 1` check).
            *   At most once when it is iterated through as `current_num + 1` within an already identified sequence.
        *   Therefore, the total work done is proportional to the number of elements `N`, leading to an overall **O(N)** time complexity.

*   **Space Complexity: O(N)**
    1.  The `num_set` stores all unique elements from the input `nums` array. In the worst case (all elements are unique), it will store `N` elements.
    2.  This results in **O(N)** space complexity for the hash set.

### Real-World Applications

The "Longest Consecutive Sequence" problem, and the underlying pattern of using hash sets for efficient lookups and sequence detection, has several real-world applications:

1.  **Data Analysis and Signal Processing**: Identifying continuous trends or patterns in datasets where data points are not necessarily sorted but need to be analyzed for consecutive values. For instance, detecting prolonged periods of a certain condition from sensor data.
2.  **Database Indexing and Query Optimization**: In some database systems, efficiently finding ranges of consecutive IDs or values can improve query performance. This pattern can inform the design of such lookup mechanisms.
3.  **Resource Allocation**: In systems managing contiguous resources (e.g., memory blocks, IP addresses), finding the longest consecutive block of available resources is a common task.
4.  **Genomics and Bioinformatics**: Identifying consecutive gene sequences or protein domains in a large, unsorted set of genetic markers.
5.  **Network Routing**: Finding consecutive IP addresses in a routing table for efficient aggregation.
6.  **Compiler Design**: Detecting sequences of related tokens or instructions.
7.  **Technical Interviews**: This problem is a common and important question in technical interviews at major tech companies (like Google, Amazon, Facebook), testing a candidate's understanding of arrays, hash tables, and time complexity optimization.