from sympy import symbols
from sympy.logic.boolalg import And, Or, Not, Implies, to_cnf

def disCombine(op, clause):
    """Helper function to decompose a clause."""
    if clause.func == Or:
        return list(clause.args)
    else:
        return [clause]

def negativeInside(literal):
    """Helper function to find the negation of a literal."""
    return Not(literal)

def toUnique(lst):
    """Helper function to remove duplicates from a list."""
    return list(set(lst))

def combine(op, lst):
    """Helper function to combine a list of literals into a clause."""
    if len(lst) == 0:
        return Or()
    elif len(lst) == 1:
        return lst[0]
    else:
        return Or(*lst)

def pl_resolve(ci, cj):
    """
    Returns all clauses that can be obtained from clauses ci and cj.
    """
    clauses = []
    for di in disCombine('or', ci):
        for dj in disCombine('or', cj):
            if di == negativeInside(dj) or negativeInside(di) == dj:
                diNew = disCombine('or', ci)
                diNew.remove(di)
                djNew = disCombine('or', cj)
                djNew.remove(dj)
                dNew = diNew + djNew
                dNew = toUnique(dNew)
                toAddD = combine('or', dNew)
                clauses.append(toAddD)
    return clauses


def pl_resolution(KB, alpha):
    """Propositional-logic resolution: say if alpha follows from KB."""
    clauses = set(KB + conjuncts(to_cnf(Not(alpha))))
    while True:
        new = set()
        pairs = [(ci, cj) for ci in clauses for cj in clauses if ci != cj]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if Or() in resolvents:  # Điều kiện rỗng biểu thị mâu thuẫn
                return True
            new = new.union(resolvents)
        if new.issubset(clauses):
            return False
        clauses = clauses.union(new)

def conjuncts(expr):
    """Chuyển đổi biểu thức thành danh sách các mệnh đề (clauses) trong CNF."""
    if isinstance(expr, And):
        return list(expr.args)
    else:
        return [expr]

class WumpusKB:
    def __init__(self):
        self.kb = set()
        self.variables = {}

    def add_breeze_rule(self, x, y):
        # Tạo biến cho Breeze và Pit
        breeze = self.get_symbol(f"Breeze_{x}_{y}")
        pit_up = self.get_symbol(f"Pit_{x}_{y+1}")
        pit_down = self.get_symbol(f"Pit_{x}_{y-1}")
        pit_left = self.get_symbol(f"Pit_{x-1}_{y}")
        pit_right = self.get_symbol(f"Pit_{x+1}_{y}")

        # Tạo quy tắc logic
        rule = Implies(breeze, Or(pit_up, pit_down, pit_left, pit_right))

        # Thêm quy tắc vào knowledge base
        self.kb.add(rule)

    def add_breeze_percept(self, x, y):
        breeze = self.get_symbol(f"Breeze_{x}_{y}")
        self.kb.add(breeze)
        self.add_breeze_rule(x, y)

    def get_symbol(self, name):
        if name not in self.variables:
            self.variables[name] = symbols(name)
        return self.variables[name]

    def get_kb(self):
        return self.kb

    def display_kb(self):
        for expr in self.kb:
            print(expr)

# Ví dụ sử dụng
kb = WumpusKB()

# Thêm các mệnh đề dựa trên môi trường
kb.add_breeze_percept(1, 1)
kb.add_breeze_percept(2, 2)

# Hiển thị các mệnh đề trong knowledge base
kb.display_kb()


# Ví dụ sử dụng
A, B, C, D, E = symbols('A11 B21 C31 D45 E67')

# Định nghĩa cơ sở tri thức KB và mệnh đề alpha
KB = [
    to_cnf(Or(A, B, C, D)),
    to_cnf(Not(D)),
]

print(KB[0].args)
alpha = (Not(D))

# Kiểm tra xem alpha có thể suy ra từ KB hay không
result = pl_resolution(KB, alpha)
print("alpha có thể suy ra từ KB" if result else "alpha không thể suy ra từ KB")
