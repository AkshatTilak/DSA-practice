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

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# Instead of using the Strategy pattern, this approach uses a single class with conditional 
# logic (if-else) to determine the payment method. This violates the Open/Closed Principle 
# because adding a new payment method requires modifying the OrderProcessor class.

class NaiveOrderProcessor:
    def process(self, amount: float, payment_method: str) -> str:
        if payment_method == "CreditCard":
            return f'Paid {amount} using Credit Card'
        elif payment_method == "PayPal":
            return f'Paid {amount} using PayPal'
        else:
            return "Unsupported payment method"

def PaymentStrategy_naive():
    processor = NaiveOrderProcessor()
    return processor.process(100.0, "CreditCard")

# --- APPROACH 2: Optimal (Strategy Design Pattern) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# This approach implements the Strategy Pattern using an abstract base class (ABC).
# It decouples the payment logic from the OrderProcessor, allowing new payment methods 
# to be added without modifying existing code (Open/Closed Principle). It also allows 
# changing the payment strategy dynamically at runtime.

from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> str:
        """Abstract method to define the payment interface."""
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> str:
        return f'Paid {amount} using Credit Card'

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: float) -> str:
        return f'Paid {amount} using PayPal'

class OrderProcessor:
    def __init__(self, strategy: PaymentStrategy):
        """Initializes the processor with a specific payment strategy."""
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy):
        """Allows changing the payment strategy at runtime."""
        self._strategy = strategy

    def process(self, amount: float) -> str:
        """Processes the payment using the current strategy."""
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        return self._strategy.pay(amount)

def PaymentStrategy_optimal():
    # Example of dynamic usage
    cc_strategy = CreditCardPayment()
    paypal_strategy = PayPalPayment()
    
    processor = OrderProcessor(cc_strategy)
    res1 = processor.process(100.0) # Paid 100.0 using Credit Card
    
    processor.set_strategy(paypal_strategy)
    res2 = processor.process(200.0) # Paid 200.0 using PayPal
    
    return res1, res2

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package design_patterns;

import java.util.Objects;

/**
 * Strategy Pattern implementation for dynamic payment billing.
 */

// Strategy Interface
interface PaymentStrategy {
    String pay(double amount);
}

// Concrete Strategy 1
class CreditCardPayment implements PaymentStrategy {
    @Override
    public String pay(double amount) {
        return String.format("Paid %.2f using Credit Card", amount);
    }
}

// Concrete Strategy 2
class PayPalPayment implements PaymentStrategy {
    @Override
    public String pay(double amount) {
        return String.format("Paid %.2f using PayPal", amount);
    }
}

// Context Class
class OrderProcessor {
    private PaymentStrategy strategy;

    public OrderProcessor(PaymentStrategy strategy) {
        this.strategy = Objects.requireNonNull(strategy, "Payment strategy cannot be null");
    }

    public void setStrategy(PaymentStrategy strategy) {
        this.strategy = Objects.requireNonNull(strategy, "Payment strategy cannot be null");
    }

    public String process(double amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        return strategy.pay(amount);
    }
}

public class StrategyPattern {
    public static void main(String[] args) {
        PaymentStrategy creditCard = new CreditCardPayment();
        PaymentStrategy payPal = new PayPalPayment();

        OrderProcessor processor = new OrderProcessor(creditCard);
        System.out.println(processor.process(100.0)); // Paid 100.00 using Credit Card

        processor.setStrategy(payPal);
        System.out.println(processor.process(200.0)); // Paid 200.00 using PayPal
    }
}
"""
