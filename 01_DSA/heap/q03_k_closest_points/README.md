# K Closest Points to Origin

## 1. Overview & Problem Explanation

The goal of this challenge is to identify the **K closest points** to the origin $(0, 0)$ from a given list of coordinates on a 2D plane. 

### The Problem Statement
Given an array of `points` where `points[i] = [x, y]` and an integer `k`, return the `k` closest points to the origin. The distance between two points $(x_1, y_1)$ and $(x_2, y_2)$ is the **Euclidean distance**:
$$\text{Distance} = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$

Since we are measuring distance from the origin $(0, 0)$, the formula simplifies to:
$$\text{Distance} = \sqrt{x^2 + y^2}$$

### Key Insight: Squared Distance
When comparing distances, calculating the square root is computationally expensive and unnecessary. If $A^2 < B^2$, then $A < B$ (for non-negative values). Therefore, we can compare the **squared distances** ($x^2 + y^2$) to achieve the same result more efficiently.

### Inputs & Constraints
- **Input**: `points` (List of lists of integers), `k` (Integer).
- **Output**: `List[List[int]]` containing the $k$ closest points.
- **Constraints**: 
    - The number of points can be up to $10^4$.
    - Coordinates can be negative.
    - $1 \le k \le \text{number of points}$.

---

## 2. Core Concepts & Data Structures

### Priority Queue (Heap)
The most efficient way to track the "top K" or "bottom K" elements in a dataset is using a **Heap**. 

- **Min-Heap**: The smallest element is always at the root. Useful if we want to extract the absolute smallest elements one by one.
- **Max-Heap**: The largest element is always at the root. This is the **optimal choice** for "K Closest" problems. 

**Why a Max-Heap for "K Closest"?**
If we want the $K$ smallest distances, we maintain a Max-Heap of size $K$. As we iterate through the points:
1. We add points to the heap.
2. Once the heap reaches size $K$, the root (the maximum value currently in our "closest" set) is the "worst" of the best.
3. If we find a new point that is closer than the root of the Max-Heap, we remove the root and insert the new point.
4. This ensures that at the end, the heap contains the $K$ smallest distances encountered.

### Quickselect Algorithm
Quickselect is a selection algorithm based on the **QuickSort** partitioning logic. Instead of sorting the entire array ($O(N \log N)$), it partitions the array around a pivot until the $K$-th element is in its final sorted position. Everything to the left of that position is guaranteed to be smaller (closer), though not necessarily sorted.

---

## 3. Step-by-Step Logic

### Approach 1: Sorting (Naive)
1. Calculate the squared distance for every point.
2. Sort the list of points based on this distance in ascending order.
3. Return the first $k$ elements.
*   **Dry Run**: `points = [[1,3], [-2,2]], k = 1` $\rightarrow$ Distances: `[10, 8]`. Sorted: `[8, 10]`. Result: `[[-2, 2]]`.

### Approach 2: Max-Heap (Optimal for Streaming/Large Data)
1. Initialize an empty Max-Heap.
2. For each point $(x, y)$:
    - Calculate squared distance $d = x^2 + y^2$.
    - Push $(-d, x, y)$ into the heap (Python's `heapq` is a Min-Heap, so we negate the distance to simulate a Max-Heap).
    - If the heap size exceeds $k$, pop the root (the point with the largest distance among the $k+1$ points).
3. After processing all points, the heap contains the $k$ closest points.
4. Extract the points from the heap and return them.

### Approach 3: Quickselect (Theoretically Fastest)
1. Pick a random pivot point.
2. Partition the array: move points closer than the pivot to the left, and points further to the right.
3. Check the index of the pivot:
    - If `index == k`, we have found the $k$ closest points.
    - If `index < k`, repeat the process on the right partition.
    - If `index > k`, repeat the process on the left partition.

---

## 4. Complexity Analysis

| Approach | Time Complexity | Space Complexity | Reasoning |
| :--- | :--- | :--- | :--- |
| **Sorting** | $O(N \log N)$ | $O(N)$ or $O(\log N)$ | Sorting the entire array of $N$ points. |
| **Max-Heap** | $O(N \log k)$ | $O(k)$ | We process $N$ points, and each heap operation takes $\log k$. |
| **Quickselect**| $O(N)$ average | $O(1)$ | On average, we discard half the search space each iteration. |

**Note on Space**: The Max-Heap approach is highly memory-efficient when $k \ll N$, as we only ever store $k$ elements.

---

## 5. Implementation

```python
import heapq

def solve_optimal(points, k):
    # We use a Max-Heap to keep track of the K closest points.
    # Python's heapq is a Min-Heap, so we store negative distances.
    max_heap = []
    
    for (x, y) in points:
        # Calculate squared Euclidean distance
        dist = -(x**2 + y**2) 
        
        if len(max_heap) < k:
            heapq.heappush(max_heap, (dist, x, y))
        else:
            # If current point is closer than the furthest point in our top K
            if dist > max_heap[0][0]: 
                heapq.heapreplace(max_heap, (dist, x, y))
    
    # Extract points from the heap
    return [[x, y] for (dist, x, y) in max_heap]

# Example usage:
# points = [[1,3],[-2,2]], k = 1 -> [[-2,2]]
# points = [[3,3],[5,-1],[-2,4]], k = 2 -> [[3,3],[-2,4]]
```

---

## 6. Real-World Applications

1. **Geolocation Services**: When you search for "Restaurants near me" on Google Maps or Yelp, the system uses a spatial index (like a QuadTree or Geohash) and then often a $k$-nearest neighbor (KNN) approach to find the closest physical locations.
2. **Recommendation Systems**: Collaborative filtering often represents users or items as vectors in a high-dimensional space. Finding the "closest" vectors (using Euclidean or Cosine distance) helps suggest similar products or movies.
3. **K-Nearest Neighbors (KNN) Algorithm**: In Machine Learning, the KNN classifier predicts the label of a data point by finding the $k$ closest training examples in the feature space.
4. **Collision Detection in Games**: To optimize physics calculations, engines find the closest objects to a player to determine which objects need active collision checking.