"""
Challenge: q02_strategy_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/strategy

Problem:
Implement Strategy pattern for dynamic payment billing integrations.
"""

# --- STARTER TEMPLATE FOR USER ---
class PaymentStrategy:
    def pay(self, amount: float) -> str:
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> str:
        return f'Paid {amount} using Credit Card'

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: float) -> str:
        return f'Paid {amount} using PayPal'

class OrderProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    def process(self, amount: float) -> str:
        return self.strategy.pay(amount)

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# Strategy pattern bindings
