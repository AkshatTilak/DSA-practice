"""
Challenge: q04_k_means
Difficulty: Medium
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Cluster iterative centroids.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(I * k * n * d)
# Space Complexity: O(k * d + n)
# This approach implements the basic Lloyd's algorithm using standard Python lists and loops.
# It uses random initialization by picking k random points from the dataset.
import math
import random

def solve_naive(X, k, max_iters=100):
    if not X or k <= 0:
        return [], []
    
    n = len(X)
    d = len(X[0])
    
    # Randomly initialize centroids from the data points
    centroids = random.sample(X, k)
    labels = [0] * n
    
    for _ in range(max_iters):
        # Assignment Step: Assign each point to the nearest centroid
        changed = False
        for i in range(n):
            min_dist = float('inf')
            best_cluster = 0
            for j in range(k):
                # Euclidean distance calculation
                dist = math.sqrt(sum((X[i][m] - centroids[j][m])**2 for m in range(d)))
                if dist < min_dist:
                    min_dist = dist
                    best_cluster = j
            
            if labels[i] != best_cluster:
                labels[i] = best_cluster
                changed = True
        
        if not changed:
            break
            
        # Update Step: Recalculate centroids as the mean of assigned points
        new_centroids = [[0.0] * d for _ in range(k)]
        counts = [0] * k
        
        for i in range(n):
            cluster = labels[i]
            counts[cluster] += 1
            for m in range(d):
                new_centroids[cluster][m] += X[i][m]
        
        for j in range(k):
            if counts[j] > 0:
                for m in range(d):
                    new_centroids[j][m] /= counts[j]
            else:
                # If a cluster becomes empty, re-initialize it to a random point
                new_centroids[j] = random.choice(X)
                
        centroids = new_centroids
        
    return centroids, labels

# --- APPROACH 2: Optimal (K-Means++ with NumPy) ---
# Time Complexity: O(I * k * n * d)
# Space Complexity: O(k * d + n)
# This approach is optimal because it uses NumPy for vectorized distance calculations, 
# significantly reducing the overhead of Python loops. Additionally, it implements 
# K-Means++ initialization, which ensures faster convergence and a better final 
# clustering result by spreading out the initial centroids.
import numpy as np

def solve_optimal(X, k, max_iters=100):
    X = np.array(X)
    n, d = X.shape
    
    if n == 0 or k <= 0:
        return [], []

    # K-Means++ Initialization
    centroids = np.empty((k, d))
    # 1. Pick the first centroid randomly from X
    centroids[0] = X[np.random.randint(n)]
    
    for i in range(1, k):
        # Compute distance from each point to the nearest already chosen centroid
        # Use squared Euclidean distance
        distances = np.min([np.sum((X - c)**2, axis=1) for c in centroids[:i]], axis=0)
        # Select next centroid with probability proportional to D(x)^2
        probs = distances / np.sum(distances)
        cumulative_probs = np.cumsum(probs)
        r = np.random.rand()
        idx = np.searchsorted(cumulative_probs, r)
        centroids[i] = X[idx]

    labels = np.zeros(n, dtype=int)
    
    for _ in range(max_iters):
        # Assignment Step (Vectorized)
        # Compute distances from all points to all centroids: (n, k)
        # dist(a, b)^2 = |a|^2 + |b|^2 - 2ab
        dist_sq = np.sum(X**2, axis=1)[:, np.newaxis] + np.sum(centroids**2, axis=1) - 2 * np.dot(X, centroids.T)
        new_labels = np.argmin(dist_sq, axis=1)
        
        if np.array_equal(labels, new_labels):
            break
        labels = new_labels
        
        # Update Step (Vectorized)
        new_centroids = np.array([X[labels == i].mean(axis=0) if np.any(labels == i) 
                                  else X[np.random.randint(n)] for i in range(k)])
        centroids = new_centroids

    return centroids.tolist(), labels.tolist()

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package classical_ml;

import java.util.*;

public class KMeans {
    public static class Result {
        public double[][] centroids;
        public int[] labels;

        public Result(double[][] centroids, int[] labels) {
            this.centroids = centroids;
            this.labels = labels;
        }
    }

    public static Result solve(double[][] X, int k, int maxIters) {
        if (X == null || X.length == 0 || k <= 0) return null;
        int n = X.length;
        int d = X[0].length;
        
        // K-Means++ Initialization
        double[][] centroids = new double[k][d];
        Random rand = new Random();
        centroids[0] = X[rand.nextInt(n)].clone();
        
        for (int i = 1; i < k; i++) {
            double[] minDistSq = new double[n];
            double sumMinDistSq = 0;
            for (int j = 0; j < n; j++) {
                double minSq = Double.MAX_VALUE;
                for (int c = 0; c < i; c++) {
                    double distSq = 0;
                    for (int m = 0; m < d; m++) {
                        distSq += Math.pow(X[j][m] - centroids[c][m], 2);
                    }
                    minSq = Math.min(minSq, distSq);
                }
                minDistSq[j] = minSq;
                sumMinDistSq += minSq;
            }
            
            double target = rand.nextDouble() * sumMinDistSq;
            double currentSum = 0;
            for (int j = 0; j < n; j++) {
                currentSum += minDistSq[j];
                if (currentSum >= target) {
                    centroids[i] = X[j].clone();
                    break;
                }
            }
        }

        int[] labels = new int[n];
        for (int iter = 0; iter < maxIters; iter++) {
            boolean changed = false;
            
            // Assignment
            for (int i = 0; i < n; i++) {
                double minDist = Double.MAX_VALUE;
                int bestCluster = 0;
                for (int j = 0; j < k; j++) {
                    double distSq = 0;
                    for (int m = 0; m < d; m++) {
                        distSq += Math.pow(X[i][m] - centroids[j][m], 2);
                    }
                    if (distSq < minDist) {
                        minDist = distSq;
                        bestCluster = j;
                    }
                }
                if (labels[i] != bestCluster) {
                    labels[i] = bestCluster;
                    changed = true;
                }
            }
            
            if (!changed) break;
            
            // Update
            double[][] newCentroids = new double[k][d];
            int[] counts = new int[k];
            for (int i = 0; i < n; i++) {
                int cluster = labels[i];
                counts[cluster]++;
                for (int m = 0; m < d; m++) {
                    newCentroids[cluster][m] += X[i][m];
                }
            }
            
            for (int j = 0; j < k; j++) {
                if (counts[j] > 0) {
                    for (int m = 0; m < d; m++) {
                        newCentroids[j][m] /= counts[j];
                    }
                } else {
                    newCentroids[j] = X[rand.nextInt(n)].clone();
                }
            }
            centroids = newCentroids;
        }
        
        return new Result(centroids, labels);
    }
}
"""
