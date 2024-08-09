from sympy import symbols, satisfiable
from sympy.logic.boolalg import Not, And, Or, Implies, Equivalent

class WumpusKB:
    def __init__(self):
        self.KB = set()
    
    def add_clause(self, clause):
        self.KB.add(clause)
    
    def infer(self, alpha):
        combined_expr = And(*self.KB, Not(alpha))
        return not satisfiable(combined_expr)
        
    def delete_clause(self, clause):
        if clause in self.KB:
            self.KB.remove(clause)

    def print_KB(self):
        print("Current Knowledge Base:")
        print(", ".join(map(str, self.KB)))
# # Define custom variables
# P11, W12, P21, P12 = symbols('P11 W12 P21 P12')

# # Example usage:
# kb = WumpusKB()
# kb.add_clause(Or(Not(P11), W12))  # Example clause: -P11 or W12
# kb.add_clause(P11)  # Example clause: -W12 or P12

# # Trying to infer if P12 is true
# print(kb.infer(W12))  # Output should be True if P12 can be inferred from the KB

# # Delete a clause
# kb.delete_clause(Or(Not(P11), W12))
    