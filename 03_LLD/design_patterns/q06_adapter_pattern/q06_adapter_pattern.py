"""
Challenge: q06_adapter_pattern
Difficulty: Medium
Link: https://refactoring.guru/design-patterns/adapter

Problem:
Translate interface adapter.
"""

# --- STARTER TEMPLATE FOR USER ---
def solve():
    # Write your solution here
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# The naive approach avoids using a formal interface (ABC) and simply creates a 
# wrapper class that delegates calls. It lacks type safety and doesn't 
# enforce a contract, making it fragile in larger systems.

class LegacyTranslator:
    """The Adaptee: A class with an incompatible interface."""
    def old_translate(self, text: str) -> str:
        return f"[Legacy] {text} translated"

class NaiveTranslatorAdapter:
    """The Adapter: A simple wrapper without a formal interface."""
    def __init__(self, legacy_translator: LegacyTranslator):
        self.legacy_translator = legacy_translator

    def translate(self, text: str) -> str:
        # Direct delegation without adhering to a target interface contract
        return self.legacy_translator.old_translate(text)

def solve_naive():
    # Usage example
    legacy = LegacyTranslator()
    adapter = NaiveTranslatorAdapter(legacy)
    print(adapter.translate("Hello World"))

# --- APPROACH 2: Optimal (Object Adapter Pattern) ---
# Time Complexity: O(1)
# Space Complexity: O(1)
# This is the optimal approach as it implements the formal Object Adapter Pattern.
# It uses an Abstract Base Class (ABC) to define a 'Target' interface, ensuring 
# that all adapters and modern implementations are interchangeable (Liskov Substitution Principle).
# This allows the client to remain decoupled from the concrete implementation 
# of the translation logic.

from abc import ABC, abstractmethod

class Translator(ABC):
    """The Target interface that the client expects."""
    @abstractmethod
    def translate(self, text: str) -> str:
        pass

class ModernTranslator(Translator):
    """A concrete implementation of the Target interface."""
    def translate(self, text: str) -> str:
        return f"[Modern] {text} translated"

class LegacyTranslator:
    """The Adaptee: A class with a different interface that we need to adapt."""
    def old_translate(self, text: str) -> str:
        return f"[Legacy] {text} translated"

class TranslatorAdapter(Translator):
    """
    The Adapter: Implements the Target interface and wraps the Adaptee.
    It converts the interface of the LegacyTranslator into the Translator interface.
    """
    def __init__(self, legacy_translator: LegacyTranslator):
        self._legacy_translator = legacy_translator

    def translate(self, text: str) -> str:
        # Adapting the call from translate() to old_translate()
        return self._legacy_translator.old_translate(text)

def solve_optimal():
    # The client code only knows about the Translator interface
    def client_code(translator: Translator, text: str):
        print(translator.translate(text))

    modern = ModernTranslator()
    legacy = LegacyTranslator()
    adapter = TranslatorAdapter(legacy)

    client_code(modern, "Hello Modern")  # Works directly
    client_code(adapter, "Hello Legacy") # Works through adapter

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package design_patterns;

/**
 * Java implementation of the Object Adapter Pattern.
 */
interface Translator {
    String translate(String text);
}

class ModernTranslator implements Translator {
    @Override
    public String translate(String text) {
        return "[Modern] " + text + " translated";
    }
}

class LegacyTranslator {
    public String oldTranslate(String text) {
        return "[Legacy] " + text + " translated";
    }
}

class TranslatorAdapter implements Translator {
    private final LegacyTranslator legacyTranslator;

    public TranslatorAdapter(LegacyTranslator legacyTranslator) {
        this.legacyTranslator = legacyTranslator;
    }

    @Override
    public String translate(String text) {
        // Adapting the incompatible call
        return legacyTranslator.oldTranslate(text);
    }
}

public class AdapterPattern {
    public static void clientCode(Translator translator, String text) {
        System.out.println(translator.translate(text));
    }

    public static void main(String[] args) {
        Translator modern = new ModernTranslator();
        LegacyTranslator legacy = new LegacyTranslator();
        Translator adapter = new TranslatorAdapter(legacy);

        clientCode(modern, "Hello Modern");
        clientCode(adapter, "Hello Legacy");
    }
}
"""
