"""
Challenge: q01_parking_lot
Difficulty: Hard
Link: https://www.geeksforgeeks.org/design-parking-lot-low-level-design/

Problem:
Design object models for multi-level parking lot including spot size constraints, ticket calculations.
"""

# --- STARTER TEMPLATE FOR USER ---
class SpotType:
    SMALL, COMPACT, LARGE = 1, 2, 3

class ParkingSpot:
    def __init__(self, id, spot_type):
        self.id = id
        self.spot_type = spot_type
        self.is_free = True

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Parking lot designs
