INFO = {
    'difficulty': 'Medium',
    'link': 'https://refactoring.guru/design-patterns/strategy',
    'description': 'Implement Strategy pattern for dynamic payment billing integrations.',
    'groups': ['Behavioral Patterns'],
    'starter_code': "class PaymentStrategy:\n    def pay(self, amount: float) -> str:\n        pass\n\nclass CreditCardPayment(PaymentStrategy):\n    def pay(self, amount: float) -> str:\n        return f'Paid {amount} using Credit Card'\n\nclass PayPalPayment(PaymentStrategy):\n    def pay(self, amount: float) -> str:\n        return f'Paid {amount} using PayPal'\n\nclass OrderProcessor:\n    def __init__(self, strategy: PaymentStrategy):\n        self.strategy = strategy\n    def process(self, amount: float) -> str:\n        return self.strategy.pay(amount)",
    'solutions': '# Strategy pattern bindings',
    'test_code': 'def test_strategy():\n    pass',
    'readme_content': '# Strategy Pattern\nBehavioral encapsulation.',
}
