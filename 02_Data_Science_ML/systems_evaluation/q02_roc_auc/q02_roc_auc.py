"""
Challenge: q02_roc_auc
Difficulty: Hard
Link: https://www.geeksforgeeks.org/data-science-interview-questions-and-answers/

Problem:
Approximate Area Under ROC.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N_pos * N_neg)
# Space Complexity: O(1)
# This approach implements the probabilistic interpretation of AUC: the probability that a randomly chosen 
# positive instance is ranked higher than a randomly chosen negative instance. 
# It iterates through every pair of positive and negative samples and counts how often the positive 
# sample's score is higher, adding 0.5 for ties.
def compute_roc_auc(y_true, y_scores):
    positives = [score for label, score in zip(y_true, y_scores) if label == 1]
    negatives = [score for label, score in zip(y_true, y_scores) if label == 0]
    
    if not positives or not negatives:
        return 0.0
    
    count = 0
    for p in positives:
        for n in negatives:
            if p > n:
                count += 1
            elif p == n:
                count += 0.5
                
    return count / (len(positives) * len(negatives))

# --- APPROACH 2: Optimal (Mann-Whitney U Statistic) ---
# Time Complexity: O(N log N)
# Space Complexity: O(N)
# This approach leverages the relationship between the Area Under the ROC Curve and the Mann-Whitney U statistic.
# By sorting the scores and calculating the rank sum of the positive samples, we can compute the AUC 
# in linearithmic time. It correctly handles ties by assigning the average rank to identical scores, 
# which is mathematically equivalent to the trapezoidal rule used in ROC analysis.
def compute_roc_auc(y_true, y_scores):
    n = len(y_true)
    if n == 0:
        return 0.0
    
    # Pair labels with scores and sort by score ascending
    data = sorted(zip(y_scores, y_true), key=lambda x: x[0])
    
    pos_count = sum(y_true)
    neg_count = n - pos_count
    
    if pos_count == 0 or neg_count == 0:
        return 0.0
    
    rank_sum = 0.0
    i = 0
    while i < n:
        # Identify blocks of tied scores
        start_idx = i
        while i + 1 < n and data[i+1][0] == data[start_idx][0]:
            i += 1
        
        # Average rank for the block: (start_rank + end_rank) / 2
        # Ranks are 1-indexed. Rank of index j is j + 1.
        # Sum of ranks from (start_idx + 1) to (i + 1) is:
        # ((start_idx + 1) + (i + 1)) * (i - start_idx + 1) / 2
        # The average rank is (start_idx + 1 + i + 1) / 2
        avg_rank = (start_idx + 1 + i + 1) / 2.0
        
        # Count how many positives are in this tied block
        pos_in_block = sum(data[j][1] for j in range(start_idx, i + 1))
        rank_sum += pos_in_block * avg_rank
        i += 1
        
    # AUC = (RankSum_pos - (n_pos * (n_pos + 1) / 2)) / (n_pos * n_neg)
    auc = (rank_sum - (pos_count * (pos_count + 1) / 2.0)) / (pos_count * neg_count)
    return auc

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package systems_evaluation;

import java.util.*;

public class RocAuc {
    /**
     * Computes the Area Under the ROC Curve using the Mann-Whitney U statistic.
     * Time Complexity: O(N log N)
     * Space Complexity: O(N)
     */
    public static double computeRocAuc(int[] yTrue, double[] yScores) {
        int n = yTrue.length;
        if (n == 0) return 0.0;

        // Create pairs of (score, label)
        Sample[] samples = new Sample[n];
        int posCount = 0;
        for (int i = 0; i < n; i++) {
            samples[i] = new Sample(yScores[i], yTrue[i]);
            if (yTrue[i] == 1) posCount++;
        }
        int negCount = n - posCount;

        if (posCount == 0 || negCount == 0) return 0.0;

        // Sort by score ascending
        Arrays.sort(samples, Comparator.comparingDouble(s -> s.score));

        double rankSum = 0.0;
        int i = 0;
        while (i < n) {
            int startIdx = i;
            while (i + 1 < n && samples[i + 1].score == samples[startIdx].score) {
                i++;
            }

            // Average rank for the tied block (1-indexed)
            double avgRank = (startIdx + 1 + i + 1) / 2.0;
            
            int posInBlock = 0;
            for (int j = startIdx; j <= i; j++) {
                if (samples[j].label == 1) posInBlock++;
            }
            
            rankSum += posInBlock * avgRank;
            i++;
        }

        return (rankSum - (posCount * (posCount + 1.0) / 2.0)) / ((double) posCount * negCount);
    }

    private static class Sample {
        double score;
        int label;
        Sample(double score, int label) {
            this.score = score;
            this.label = label;
        }
    }

    public static void main(String[] args) {
        int[] yTrue = {0, 0, 1, 1};
        double[] yScores = {0.1, 0.4, 0.35, 0.8};
        System.out.println(computeRocAuc(yTrue, yScores)); // Expected: 0.75
    }
}
"""
