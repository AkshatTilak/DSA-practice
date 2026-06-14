"""
Challenge: q03_koko_eating_bananas
Difficulty: Medium
Link: https://leetcode.com/problems/koko-eating-bananas/

Problem:
Find the minimum rate to eat all piles within H hours.
"""

# --- STARTER TEMPLATE FOR USER ---
def min_eating_speed(piles: list[int], h: int) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
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
"""
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
"""
