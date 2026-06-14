"""
Challenge: q03_evaluate_reverse_polish_notation
Difficulty: Medium
Link: https://leetcode.com/problems/evaluate-reverse-polish-notation/

Problem:
Evaluate RPN mathematical expression.
"""

# --- STARTER TEMPLATE FOR USER ---
def eval_rpn(tokens: list[str]) -> int:
    pass

# =====================================================================
# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS
# =====================================================================

# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(N^2)
# Space Complexity: O(N)
# This approach simulates the evaluation by repeatedly scanning the token list for the first operator encountered.
# Once an operator is found, it evaluates the two preceding operands and replaces the three tokens (operand, operand, operator) 
# with the result. This process is repeated until only one value remains. It is naive because it involves 
# frequent list modifications and repeated scans.
def eval_rpn_naive(tokens: list[str]) -> int:
    # Create a copy to avoid modifying the input list
    expr = tokens[:]
    
    while len(expr) > 1:
        for i in range(len(expr)):
            if expr[i] in {"+", "-", "*", "/"}:
                # The two operands are immediately to the left of the operator
                op2 = int(expr[i - 1])
                op1 = int(expr[i - 2])
                operator = expr[i]
                
                if operator == '+':
                    res = op1 + op2
                elif operator == '-':
                    res = op1 - op2
                elif operator == '*':
                    res = op1 * op2
                else: # division
                    # Using int(a / b) to ensure truncation towards zero
                    res = int(op1 / op2)
                
                # Replace the [op1, op2, operator] sequence with the result
                expr[i - 2 : i + 1] = [str(res)]
                break
                
    return int(expr[0])

# --- APPROACH 2: Optimal (Stack) ---
# Time Complexity: O(N)
# Space Complexity: O(N)
# This is the optimal approach because it processes each token exactly once. 
# A stack is used to store operands; when an operator is encountered, the top two 
# operands are popped, the operation is performed, and the result is pushed back.
# This mimics the natural evaluation order of RPN and avoids the O(N^2) overhead of 
# list manipulation seen in the naive approach.
def eval_rpn_optimal(tokens: list[str]) -> int:
    stack = []
    
    for token in tokens:
        if token not in {"+", "-", "*", "/"}:
            # Token is a number, push it to stack
            stack.append(int(token))
        else:
            # Token is an operator, pop the last two operands
            # Note: The second pop is the left operand (op1), first pop is right operand (op2)
            op2 = stack.pop()
            op1 = stack.pop()
            
            if token == '+':
                stack.append(op1 + op2)
            elif token == '-':
                stack.append(op1 - op2)
            elif token == '*':
                stack.append(op1 * op2)
            elif token == '/':
                # In Python, // is floor division (towards negative infinity).
                # RPN typically requires truncation towards zero.
                # int(op1 / op2) achieves truncation towards zero.
                stack.append(int(op1 / op2))
                
    return stack[0]

# To match the starter code signature exactly:
def eval_rpn(tokens: list[str]) -> int:
    return eval_rpn_optimal(tokens)

# --- APPROACH 3: Secondary Language (Java Variant) ---
"""
package stack;

import java.util.Stack;

public class EvaluateReversePolishNotation {
    /**
     * Evaluates the given RPN expression.
     * Time Complexity: O(N)
     * Space Complexity: O(N)
     */
    public int evalRPN(String[] tokens) {
        Stack<Integer> stack = new Stack<>();
        
        for (String token : tokens) {
            if (isOperator(token)) {
                int op2 = stack.pop();
                int op1 = stack.pop();
                
                switch (token) {
                    case "+":
                        stack.push(op1 + op2);
                        break;
                    case "-":
                        stack.push(op1 - op2);
                        break;
                    case "*":
                        stack.push(op1 * op2);
                        break;
                    case "/":
                        // In Java, integer division / already truncates towards zero
                        stack.push(op1 / op2);
                        break;
                }
            } else {
                stack.push(Integer.parseInt(token));
            }
        }
        
        return stack.pop();
    }
    
    private boolean isOperator(String token) {
        return token.equals("+") || token.equals("-") || token.equals("*") || token.equals("/");
    }
    
    public static void main(String[] args) {
        EvaluateReversePolishNotation solution = new EvaluateReversePolishNotation();
        String[] tokens = {"2", "1", "+", "3", "*"};
        System.out.println(solution.evalRPN(tokens)); // Output: 9
    }
}
"""
