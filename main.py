class Sudoku:
    def __init__(self, table, variables):
        self.neighbors = dict()
        self.constraints = list()
        self.domains = dict()
        self.table = table
        self.variables = variables
        self.pruned = dict()
        self.prepare()

    def update_pruned(self):
        for var in self.variables:
            self.pruned[var] = list()

    def build_neighbors(self):
        for x in self.variables:
            self.neighbors[x] = list()
            for c in self.constraints:
                if x == c[0]:
                    self.neighbors[x].append(c[1])

    @staticmethod
    def constraint(x, y):
        return x != y

    def prepare(self):
        self.update_pruned()
        self.update_domain()
        self.constraints = self.update_constraints()
        self.build_neighbors()

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

    def update_domain(self):
        for entity, val in self.table.items():
            if not val:
                self.domains[entity] = list(range(1, 10))
            else:
                self.domains[entity] = [val]

    def get_var_domain(self, var):
        col_unused_vals = self.get_unused_val_of_col(var=var)
        row_unused_vals = self.get_unused_val_of_row(var=var)
        square_unused_vals = self.get_unused_val_of_square(var=var)
        return list(
            col_unused_vals.intersection(row_unused_vals).intersection(square_unused_vals)
        )

    def is_ac3_solved(self):
        for var in self.variables:
            if len(self.domains[var]) > 1:
                return False
        return True

    def sort_vals(self, var):
        if len(self.domains[var]) == 1:
            return self.domains[var]
        criterion = lambda value: self.number_of_conflicts(var, value)
        return sorted(self.domains[var], key=criterion)

    def number_of_conflicts(self, var, value):
        count = 0
        for related_var in self.neighbors[var]:
            if len(self.domains[related_var]) > 1 and value in self.domains[related_var]:
                count += 1
        return count

    def is_consistent(self, assignment, var, value):
        is_consistent = True
        for current_var, current_value in assignment.items():
            if current_value == value and current_var in self.neighbors[var]:
                is_consistent = False
        return is_consistent

    def select_var(self, assignment):
        unassigned = []
        for var in self.variables:
            if var not in assignment:
                unassigned.append(var)
        criterion = lambda var: len(self.domains[var])
        return min(unassigned, key=criterion)

    def assign(self, var, value, assignment):
        assignment[var] = value

    def unassign(self, var, assignment):
        if var in assignment:
            for (assigned_var, value) in self.pruned[var]:
                self.domains[assigned_var].append(value)
            self.pruned[var] = []
            del assignment[var]

    def forward_check(self, var, value, assignment):
        for related_c in self.neighbors[var]:
            if related_c not in assignment:
                if value in self.domains[related_c]:
                    self.domains[related_c].remove(value)
                    self.pruned[var].append((related_c, value))


class Solution:
    @staticmethod
    def ac3(sudoku):

        queue = list(sudoku.constraints)

        while queue:

            xi, xj = queue.pop(0)

            if Solution.revise(sudoku, xi, xj):

                if len(sudoku.domains[xi]) == 0:
                    return False

                for xk in sudoku.neighbors[xi]:
                    if xk != xi:
                        queue.append([xk, xi])

        return True

    @staticmethod
    def revise(sudoku, xi, xj):

        revised = False

        for x in sudoku.domains[xi]:
            if not any([sudoku.constraint(x, y) for y in sudoku.domains[xj]]):
                sudoku.domains[xi].remove(x)
                revised = True

        return revised

    @staticmethod
    def backtrack(sudoku: Sudoku, assignment: dict):
        if len(assignment) == len(sudoku.variables):
            return assignment
        var = sudoku.select_var(assignment)
        vals_sorted = sudoku.sort_vals(var)
        for val in vals_sorted:
            if sudoku.is_consistent(assignment, var, val):
                sudoku.assign(var, val, assignment)
                result = Solution.backtrack(sudoku, assignment)
                if result:
                    return result
                sudoku.unassign(var, assignment)
        return False

    @staticmethod
    def print_result(sudoku: Sudoku, assignment):
        sudoku.table.update(assignment)
        res = ""
        for i in range(0, 9):
            for j in range(0, 9):
                res = res + str(sudoku.table[i, j]) + ' '
            res = res.strip()
            res = res + '\n'
        print(res)

    @classmethod
    def print_result_2(cls, sudoku):
        res = ""
        for i in range(0, 9):
            for j in range(0, 9):
                res = res + str(sudoku.domains[i, j][0]) + ' '
            res = res.strip()
            res = res + '\n'
        print(res)


def main():
    size = 9
    variables = []
    table = dict()
    for i in range(size):
        row = list(map(int, input().replace(".", "0").split(" ")))
        z = 0
        for z in range(len(row)):
            if not row[z]:
                variables.append((i, z))
            table[(i, z)] = row[z]
    sudoku = Sudoku(table, variables)
    if Solution.ac3(sudoku):
        if sudoku.is_ac3_solved():
            Solution.print_result_2(sudoku)
        else:
            assignment = dict()
            result = Solution.backtrack(sudoku=sudoku, assignment=assignment)
            Solution.print_result(sudoku, result)


if __name__ == '__main__':
    main()
