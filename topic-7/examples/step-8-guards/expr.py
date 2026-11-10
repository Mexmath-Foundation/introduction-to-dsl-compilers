"""Step 8: visitors over expressions -- the recursive case.

The visitors so far emitted lines and returned nothing; the tree was shallow
(machine > state > transition > action). A guard is an expression tree of
arbitrary depth, and the natural visitor over it *returns a value* for each
node, built from the values of its children: the C text of the sub-expression,
or its numeric value. ``visit`` already returns whatever the method returns,
so nothing in the base class changes -- only the methods now ``return``.

Three visitors share one grammar:
* ``ExprToC``  -- Expr -> str, the expression spelled in C;
* ``ExprEval`` -- Expr -> int/bool, the expression evaluated in an environment;
* ``VarCollector`` -- Expr -> set of variable names (what the C side must declare).

Every grammar level has the same shape (operands with operators between), so
each method is a fold over ``node.operands`` / ``node.ops``. Comparisons chain
left to right in both ExprToC and ExprEval (``a < b < c`` is ``(a < b) < c``),
which is C's reading, not Python's: the two translations must agree with each
other, so one semantics was chosen and written down here.
"""


class Visitor:
    def visit(self, node):
        method = getattr(self, "visit_" + type(node).__name__, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        for attr in type(node)._tx_attrs.values():
            if attr.cont and not attr.is_base_type:
                value = getattr(node, attr.name)
                for child in value if attr.mult != "1" else [value]:
                    if child is not None:
                        self.visit(child)


class ExprToC(Visitor):
    """Spell an expression in C. Sub-expressions are parenthesised when they
    have more than one operand, so the C precedence never has to be trusted."""

    def _chain(self, node, join):
        parts = [self.visit(o) for o in node.operands]
        if len(parts) == 1:
            return parts[0]
        return "(" + join(parts, getattr(node, "ops", None)) + ")"

    def visit_Or(self, n):
        return self._chain(n, lambda p, _: " || ".join(p))

    def visit_And(self, n):
        return self._chain(n, lambda p, _: " && ".join(p))

    def visit_NotExpr(self, n):
        return "!" + self.visit(n.operand)

    def visit_Cmp(self, n):
        return self._chain(n, self._interleave)

    def visit_Sum(self, n):
        return self._chain(n, self._interleave)

    def visit_Term(self, n):
        return self._chain(n, self._interleave)

    @staticmethod
    def _interleave(parts, ops):
        out = [parts[0]]
        for op, part in zip(ops, parts[1:], strict=True):
            out += [op, part]
        return " ".join(out)

    def visit_Int(self, n):
        return str(n.value)

    def visit_Var(self, n):
        return n.name


class ExprEval(Visitor):
    """Evaluate an expression in an environment: a dict of variable values."""

    OPS = {
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: int(a / b),  # C integer division
    }

    def __init__(self, env):
        self.env = env

    def _fold(self, node):
        value = self.visit(node.operands[0])
        for op, operand in zip(getattr(node, "ops", []), node.operands[1:], strict=True):
            value = self.OPS[op](int(value), int(self.visit(operand)))
        return value

    def visit_Or(self, n):
        if len(n.operands) == 1:  # a bare operand, e.g. "(count + 1)": pass the value through
            return self.visit(n.operands[0])
        return any(self.visit(o) for o in n.operands)  # short-circuit, like C

    def visit_And(self, n):
        if len(n.operands) == 1:
            return self.visit(n.operands[0])
        return all(self.visit(o) for o in n.operands)

    def visit_NotExpr(self, n):
        return not self.visit(n.operand)

    visit_Cmp = visit_Sum = visit_Term = _fold

    def visit_Int(self, n):
        return n.value

    def visit_Var(self, n):
        return self.env[n.name]  # KeyError: an undeclared variable; lecture 9's job to catch


class VarCollector(Visitor):
    """The set of variable names an expression (or a whole machine) mentions."""

    def __init__(self):
        self.names = set()

    def visit_Var(self, n):
        self.names.add(n.name)
