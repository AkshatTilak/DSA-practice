INFO = {
    'difficulty': 'Medium',
    'link': 'https://leetcode.com/problems/koko-eating-bananas/',
    'description': 'Find the minimum rate to eat all piles within H hours.',
    'groups': ['Array', 'Binary Search'],
    'starter_code': """def min_eating_speed(piles: list[int], h: int) -> int:
    pass""",
    'solutions': """# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(max(piles) * len(piles))
# Space Complexity: O(1)
# This approach iterates through every possible eating speed starting from 1 up to the maximum number of bananas in a single pile. For each speed, it calculates the total hours required to eat all piles. The first speed that allows Koko to finish within h hours is the minimum rate.
def min_eating_speed_naive(piles: list[int], h: int) -> int:
    import math
    
    # The maximum possible speed needed is the size of the largest pile
    max_pile = max(piles)
    
    # Try every speed from 1 upwards
    for k in range(1, max_pile + 1):
        total_hours = 0
        for pile in piles:
            # Calculate ceil(pile / k)
            total_hours += math.ceil(pile / k)
        
        if total_hours <= h:
            return k
            
    return max_pile

# --- APPROACH 2: Optimal (Binary Search on Answer) ---
# Time Complexity: O(len(piles) * log(max(piles)))
# Space Complexity: O(1)
# The problem exhibits a monotonic property: if Koko can finish all bananas at speed 'k', she can also finish them at any speed greater than 'k'. This allows us to binary search for the minimum speed in the range [1, max(piles)]. For each candidate speed, we perform a linear scan of the piles to check feasibility.
def min_eating_speed_optimal(piles: list[int], h: int) -> int:
    import math

    def can_finish(k: int) -> bool:
        # Calculate total hours needed at speed k
        total_hours = 0
        for pile in piles:
            # Use (pile + k - 1) // k for integer ceiling division
            total_hours += (pile + k - 1) // k
            if total_hours > h:
                return False
        return total_hours <= h

    # Search range: minimum speed 1, maximum speed is the largest pile
    low = 1
    high = max(piles)
    ans = high

    while low <= high:
        mid = (low + high) // 2
        if mid == 0: # Guard against division by zero, though low starts at 1
            low = 1
            continue
            
        if can_finish(mid):
            ans = mid      # This speed works, try to find a smaller one
            high = mid - 1
        else:
            low = mid + 1   # Speed too slow, increase it
            
    return ans

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package binary_search;

public class KokoEatingBananas {
    /**
     * Finds the minimum eating speed k to eat all bananas within h hours.
     * Time Complexity: O(N * log(M)) where N is piles.length and M is max(piles).
     * Space Complexity: O(1).
     */
    public int minEatingSpeed(int[] piles, int h) {
        int low = 1;
        int high = 0;
        
        for (int pile : piles) {
            high = Math.max(high, pile);
        }
        
        int result = high;
        
        while (low <= high) {
            int mid = low + (high - low) / 2;
            
            if (canFinish(piles, h, mid)) {
                result = mid;
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        
        return result;
    }
    
    private boolean canFinish(int[] piles, int h, int k) {
        if (k == 0) return false;
        long totalHours = 0; // Use long to prevent overflow
        for (int pile : piles) {
            // Perform ceiling division: ceil(pile / k)
            totalHours += (pile + k - 1) / k;
            if (totalHours > h) {
                return false;
            }
        }
        return totalHours <= h;
    }

    public static void main(String[] args) {
        KokoEatingBananas solver = new KokoEatingBananas();
        int[] piles = {3, 6, 7, 11};
        int h = 8;
        System.out.println("Min speed: " + solver.minEatingSpeed(piles, h)); // Expected: 4
    }
}
\"\"\"""",
    'test_code': """def test_koko():
    assert min_eating_speed([3,6,7,11], 8) == 4""",
    'readme_content': """# Koko Eating Bananas

## 📝 Overview & Problem Explanation

You are given `piles`, a list of integers representing the number of bananas in each pile, and `h`, an integer representing the total number of hours Koko has to eat all the bananas. Koko wants to eat all the bananas, but she can only eat at a constant integer speed, let's call it `k` (bananas per hour).

For each pile `piles[i]`, if Koko eats at speed `k`, it takes her `ceil(piles[i] / k)` hours to finish that pile. For example, if a pile has 7 bananas and Koko eats at speed 3, she takes `ceil(7 / 3) = ceil(2.33) = 3` hours (she eats 3 in the first hour, 3 in the second, and the remaining 1 in the third hour). She must finish a pile before moving to the next.

The goal is to find the **minimum integer eating speed `k`** such that Koko can eat all the bananas from all piles within `h` hours.

### Input
*   `piles`: A `list[int]` where `piles[i]` is the number of bananas in the `i`-th pile.
*   `h`: An `int` representing the maximum hours Koko has.

### Output
*   An `int` representing the minimum eating speed `k`.

### Constraints
*   `1 <= piles.length <= 10^4`
*   `1 <= piles[i] <= 10^9` (Pile sizes can be very large)
*   `piles.length <= h <= 10^9` (Hours available can be very large)

### Edge Cases
*   **Smallest `k`**: Koko must eat at least 1 banana per hour. So, `k` must be at least 1.
*   **Largest `k`**: If Koko eats at a speed `k` equal to or greater than the largest pile size, she will finish each pile in exactly 1 hour. Any `k` greater than `max(piles)` will still result in 1 hour per pile, so there's no benefit to eating faster than `max(piles)`. Thus, `max(piles)` is a reasonable upper bound for our search space for `k`.
*   **`h` is very large**: Koko can afford to eat very slowly, potentially even `k=1`.
*   **`h` is very small**: Koko might need to eat very quickly, up to `max(piles)` bananas per hour, to finish on time.

## 🧠 Core Concepts & Data Structures/Algorithms

The core concept for solving "Koko Eating Bananas" optimally is **Binary Search**, not on the `piles` array itself, but on the **possible range of eating speeds `k`**.

### Why Binary Search?

1.  **Monotonicity**: The problem asks for the *minimum* `k` that satisfies a certain condition (eating all bananas within `h` hours). This is a strong indicator for binary search. Let's analyze the property:
    *   If Koko can eat all bananas within `h` hours at a speed `k`, then she can *also* eat them all within `h` hours (or less) at any speed `k' > k`. Eating faster can only reduce or maintain the total time, never increase it.
    *   Conversely, if she *cannot* eat all bananas within `h` hours at speed `k`, then she certainly cannot do so at any speed `k'' < k`. Eating slower would only increase the total time.
    *   This monotonic property ("if `k` works, then anything greater than `k` also works") is fundamental for applying binary search.

2.  **Search Space**: We need to find `k` within a defined range:
    *   **Lower Bound (`low`)**: The minimum possible eating speed is 1 (Koko must eat at least 1 banana per hour).
    *   **Upper Bound (`high`)**: The maximum practical eating speed is `max(piles)`. If Koko eats faster than the largest pile, say `P_max`, she'll still spend 1 hour per pile of size `P_max` or less. There's no further time benefit beyond `k = P_max`.

Therefore, we can binary search for the optimal `k` in the range `[1, max(piles)]`.

### Helper Function: `check(k)`

To perform binary search, we need a function that, given a potential eating speed `k`, tells us if Koko can finish all bananas within `h` hours. This function will be:

```python
import math

def calculate_hours_needed(piles: list[int], k: int) -> int:
    \"\"\"
    Calculates the total hours Koko needs to eat all piles at speed k.
    \"\"\"
    total_hours = 0
    for bananas_in_pile in piles:
        # Time for one pile: ceil(bananas_in_pile / k)
        total_hours += math.ceil(bananas_in_pile / k)
    return total_hours
```

Inside our binary search, we'll call `calculate_hours_needed(piles, mid)` and compare its result with `h`.

## Walkthrough: Step-by-Step Logic

### 1. Brute Force Approach (Conceptual)

A naive approach would be to iterate through every possible eating speed `k` from 1 up to `max(piles)`. For each `k`, we would calculate the total time required using the `calculate_hours_needed` helper function. The first `k` that allows Koko to finish within `h` hours would be our answer.

**Steps:**
1. Find the maximum number of bananas in any pile, `max_bananas = max(piles)`.
2. Iterate `k` from `1` to `max_bananas`.
3. For each `k`, call `current_hours = calculate_hours_needed(piles, k)`.
4. If `current_hours <= h`, then `k` is the minimum speed found so far that works. Since we are iterating upwards, this `k` is the first one that works, and thus the minimum. Return `k`.

**Why it's not optimal:** The `max(piles)` can be up to `10^9`. Iterating through `10^9` possible values of `k` and performing `O(N)` calculations for each `k` is too slow (`10^9 * 10^4` operations is astronomically large).

### 2. Optimal Approach: Binary Search on Rates

This approach leverages the monotonicity discussed earlier.

**Steps:**
1.  **Define Search Space:**
    *   `low = 1` (Minimum possible eating speed).
    *   `high = max(piles)` (Maximum practical eating speed).
    *   `ans = high` (Initialize `ans` to a value that is guaranteed to be a valid speed, e.g., `high`, or a sentinel value like -1 if handling edge cases explicitly).

2.  **Binary Search Loop:** Continue while `low <= high`.
    *   **Calculate `mid`:** `mid = low + (high - low) // 2`. This prevents potential integer overflow compared to `(low + high) // 2` if `low` and `high` are very large.
    *   **Check Feasibility:** Call `hours_taken = calculate_hours_needed(piles, mid)`.
    *   **Adjust Search Space:**
        *   If `hours_taken <= h`:
            *   This `mid` speed *is* feasible. It could be our answer, or maybe an even smaller speed is possible.
            *   Store `mid` as a potential answer: `ans = mid`.
            *   Try to find a smaller speed: `high = mid - 1`.
        *   If `hours_taken > h`:
            *   This `mid` speed is *too slow*. Koko needs to eat faster.
            *   Discard `mid` and all speeds less than it: `low = mid + 1`.

3.  **Return Result:** After the loop terminates, `ans` will hold the minimum eating speed `k` that satisfies the condition.

### Dry Run Example

Let's use `piles = [3, 6, 7, 11]`, `h = 8`.

1.  **Initialize:**
    *   `max_bananas = 11`
    *   `low = 1`, `high = 11`
    *   `ans = 11` (or any valid upper bound)

2.  **Iteration 1:**
    *   `low = 1`, `high = 11`
    *   `mid = 1 + (11 - 1) // 2 = 6`
    *   `hours_taken = calculate_hours_needed([3, 6, 7, 11], 6)`:
        *   `ceil(3/6) = 1`
        *   `ceil(6/6) = 1`
        *   `ceil(7/6) = 2`
        *   `ceil(11/6) = 2`
        *   `Total = 1 + 1 + 2 + 2 = 6`
    *   `hours_taken (6) <= h (8)` is **True**.
    *   `ans = 6`. Try smaller speeds: `high = 6 - 1 = 5`.

3.  **Iteration 2:**
    *   `low = 1`, `high = 5`
    *   `mid = 1 + (5 - 1) // 2 = 3`
    *   `hours_taken = calculate_hours_needed([3, 6, 7, 11], 3)`:
        *   `ceil(3/3) = 1`
        *   `ceil(6/3) = 2`
        *   `ceil(7/3) = 3`
        *   `ceil(11/3) = 4`
        *   `Total = 1 + 2 + 3 + 4 = 10`
    *   `hours_taken (10) <= h (8)` is **False**.
    *   Speed `3` is too slow. Need to eat faster: `low = 3 + 1 = 4`.

4.  **Iteration 3:**
    *   `low = 4`, `high = 5`
    *   `mid = 4 + (5 - 4) // 2 = 4`
    *   `hours_taken = calculate_hours_needed([3, 6, 7, 11], 4)`:
        *   `ceil(3/4) = 1`
        *   `ceil(6/4) = 2`
        *   `ceil(7/4) = 2`
        *   `ceil(11/4) = 3`
        *   `Total = 1 + 2 + 2 + 3 = 8`
    *   `hours_taken (8) <= h (8)` is **True**.
    *   `ans = 4`. Try smaller speeds: `high = 4 - 1 = 3`.

5.  **Iteration 4:**
    *   `low = 4`, `high = 3`
    *   `low` is now `> high`. The loop terminates.

6.  **Return `ans = 4`**. This is the minimum eating speed.

```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    \"\"\"
    Finds the minimum eating speed k such that Koko can eat all piles
    within h hours.
    \"\"\"

    def calculate_hours_needed(current_k: int) -> int:
        \"\"\"
        Helper function to calculate total hours needed for a given speed k.
        \"\"\"
        total_hours = 0
        for bananas_in_pile in piles:
            # math.ceil(a / b) can be implemented as (a + b - 1) // b for positive integers
            # using math.ceil directly is clearer.
            total_hours += math.ceil(bananas_in_pile / current_k)
        return total_hours

    # Define the search space for k.
    # Minimum possible speed is 1.
    low = 1
    # Maximum practical speed is the largest pile size.
    # If k > max(piles), it still takes 1 hour per pile, no further benefit.
    high = max(piles)
    
    # This will store our answer (the minimum k).
    # Initialize it to a value that's guaranteed to be valid, e.g., high.
    min_k_found = high 

    while low <= high:
        mid_k = low + (high - low) // 2 # Calculate middle speed

        hours_taken = calculate_hours_needed(mid_k)

        if hours_taken <= h:
            # If Koko can finish within h hours at speed mid_k,
            # this mid_k is a possible answer.
            # We try to find an even smaller speed in the left half.
            min_k_found = mid_k
            high = mid_k - 1
        else:
            # If Koko cannot finish within h hours at speed mid_k,
            # then mid_k is too slow. We need to increase speed.
            # Search in the right half.
            low = mid_k + 1
            
    return min_k_found

```

## 📊 Complexity Analysis

| Approach                | Time Complexity         | Space Complexity |
| :---------------------- | :---------------------- | :--------------- |
| **Brute Force (Conceptual)** | O(max(piles) * N)        | O(1)             |
| **Optimal: Binary Search** | O(N * log(max(piles))) | O(1)             |

### Explanation of Complexities:

1.  **Brute Force (Conceptual)**:
    *   **Time Complexity**: We iterate `k` from 1 up to `max(piles)`. In the worst case, `max(piles)` can be `10^9`. For each `k`, we iterate through all `N` piles to calculate the total hours. Thus, `O(max(piles) * N)`. This is too slow for the given constraints.
    *   **Space Complexity**: We only use a few variables for `k`, `total_hours`, etc., which is constant extra space. `O(1)`.

2.  **Optimal: Binary Search**:
    *   **Time Complexity**:
        *   The binary search operates on the range `[1, max(piles)]`. The number of iterations for binary search is `log(max(piles))`. In the worst case, `max(piles)` is `10^9`, so `log(10^9)` is approximately `log2(10^9) ≈ 30`.
        *   Inside each binary search iteration, we call `calculate_hours_needed`. This function iterates through all `N` piles. So, it takes `O(N)` time.
        *   Combining these, the total time complexity is `O(N * log(max(piles)))`.
        *   Given `N <= 10^4` and `log(max(piles)) ≈ 30`, this becomes `10^4 * 30 = 3 * 10^5` operations, which is efficient enough.
    *   **Space Complexity**: We only use a few variables (`low`, `high`, `mid_k`, `ans`, `total_hours`), which require constant extra space. `O(1)`.

## 🌍 Real-World Applications

The "Koko Eating Bananas" problem, and more broadly, the pattern of **binary searching on the answer** (or a monotonic property), is very common in various real-world scenarios where you need to find an optimal threshold or rate:

1.  **Resource Allocation & Capacity Planning**:
    *   **Example**: Determining the minimum server processing power (CPU/RAM) `k` required to handle a peak load of `N` requests within `H` hours, where each request `piles[i]` demands a certain amount of processing.
    *   **Application**: Cloud resource auto-scaling, batch job scheduling, network bandwidth allocation.

2.  **Manufacturing and Production Optimization**:
    *   **Example**: Finding the slowest acceptable machine speed `k` to produce all `N` items (with varying complexities `piles[i]`) within a total production time `H`.
    *   **Application**: Assembly line optimization, project management to find the minimum effective work rate.

3.  **Logistics and Delivery**:
    *   **Example**: What's the minimum average speed `k` a fleet of delivery trucks needs to maintain to complete all `N` deliveries (each with a specific distance `piles[i]`) within `H` total working hours, considering varying road conditions or traffic?
    *   **Application**: Route optimization, fleet management systems.

4.  **Financial Modeling**:
    *   **Example**: Determining the minimum acceptable interest rate `k` for a loan portfolio to yield a total return `H` over `N` different investment instruments `piles[i]`.
    *   **Application**: Risk assessment, portfolio optimization.

This pattern is especially useful when the "check function" (determining if a given `k` is feasible) is relatively easy to compute, but iterating through all possible `k` values is too slow due to a large search space.""",
}
