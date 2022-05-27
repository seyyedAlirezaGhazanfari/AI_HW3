class Sudoku:
    def __init__(self, table: dict):
        self.table = table
        self.variables = self.update_vars()
        self.domains = dict()
        self.update_domain()
        self.constraints = self.update_constraints()
        self.neighbors = {v: list() for v in self.variables}

    def update_domain(self):
        for entity, val in self.table.items():
            if not val:
                self.domains[entity] = list(range(1, 10))
            else:
                self.domains[entity] = [val]

    def is_ac3_solved(self):
        for a in list(self.domains.values()):
            if len(a) != 1:
                return False
        return True

    @staticmethod
    def constraint(x, y):
        return x != y

    def update_constraints(self):
        constraints = list()
        for var in self.variables:
            i = var[0]
            j = var[1]
            for k in range(9):
                if k != j:
                    constraints.append((var, (i, k)))
            for k in range(9):
                if k != i:
                    constraints.append((var, (k, j)))
            for h in range(3):
                for u in range(3):
                    if (i, j) != (i - (i % 3) + h, j - (j % 3) + u):
                        constraints.append((var, (i - (i % 3) + h, j - (j % 3) + u)))
        return constraints

    def update_vars(self):
        vars = list()
        for pos, val in self.table.items():
            if not val:
                vars.append(pos)
        return vars

    def select_unassigned_var(self, param):
        diff = set(self.variables).difference(param)
        crit = lambda var: len(self.domains[var])
        return min(diff, key=crit)

    def ordered_domain(self, v):
        if len(self.domains[v]) == 1:
            return self.domains[v]
        criterion = lambda value: self.number_of_conflicts(v, value)
        return sorted(self.domains[v], key=criterion)

    def number_of_conflicts(self, var, value):
        count = 0
        for related_var in self.neighbors[var]:
            if len(self.domains[related_var]) > 1 and value in self.domains[related_var]:
                count += 1
        return count


class Solution:
    @staticmethod
    def ac_3(sudoku: Sudoku):
        constraints = set(sudoku.constraints)
        while constraints:
            x_i, x_j = constraints.pop()
            if Solution.reduction(sudoku, x_i, x_j):
                if not sudoku.domains[x_i]:
                    return False
                else:
                    for new_x in sudoku.neighbors[x_i]:
                        constraints.add((new_x, x_i))
        return True

    @staticmethod
    def reduction(sudoku: Sudoku, x_i, x_j):
        is_reduction_done = False
        for val_i in sudoku.domains[x_i]:
            is_constraints_ok = any([sudoku.constraint(val_i, j) for j in sudoku.domains[x_j]])
            if not is_constraints_ok:
                sudoku.domains[x_i].remove(val_i)
                is_reduction_done = True
        return is_reduction_done

    @staticmethod
    def get_input():
        size = 9
        table = dict()
        for i in range(size):
            row = list(map(int, input().replace(".", "0").split(" ")))
            for j in range(len(row)):
                table[(i, j)] = row[j]
        sudoku = Sudoku(table=table)
        if Solution.ac_3(sudoku):
            if sudoku.is_ac3_solved():
                pass
            assignment = dict()
            result = Solution.backtrack(sudoku, assignment)
            if result:
                Solution.print_backtrack_result(sudoku, assignment)
            else:
                return

    @staticmethod
    def print_backtrack_result(sudoku: Sudoku, assignment: dict):
        sudoku.table.update(assignment)
        res = ""
        for i in range(9):
            for j in range(9):
                res = res + str(sudoku.table.get((i, j))) + " "
            res = res.strip()
            res = res + '\n'
        print(res)

    @staticmethod
    def backtrack(sudoku: Sudoku, assignment: dict):
        if len(assignment.keys()) == len(sudoku.variables):
            return assignment
        v = sudoku.select_unassigned_var(set(assignment.keys()))
        for val in sudoku.ordered_domain(v):
            assignment[v] = val
            result = Solution.backtrack(sudoku, assignment)
            if result:
                return result
            del assignment[v]
        return {}


Solution.get_input()
