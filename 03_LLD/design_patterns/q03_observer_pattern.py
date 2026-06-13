"""
Challenge: q03_observer_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/observer

Problem:
Implement Publish-Subscribe dynamic messaging engine via Observer Pattern.
"""

# --- STARTER TEMPLATE FOR USER ---
class Subject:
    def __init__(self):
        self._observers = []
    def register(self, obs):
        self._observers.append(obs)
    def notify(self, event: str):
        for o in self._observers: o.update(event)

class Observer:
    def update(self, event: str):
        pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Observer implementations
