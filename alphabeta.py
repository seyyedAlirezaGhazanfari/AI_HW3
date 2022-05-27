import math
from player import Player


class Imagination:
    WEIGHTS = [4, -3, 2, 2, 2, 2, -3, 4,
               -3, -4, -1, -1, -1, -1, -4, -3,
               2, -1, 1, 0, 0, 1, -1, 2,
               2, -1, 0, 1, 1, 0, -1, 2,
               2, -1, 0, 1, 1, 0, -1, 2,
               2, -1, 1, 0, 0, 1, -1, 2,
               -3, -4, -1, -1, -1, -1, -4, -3,
               4, -3, 2, 2, 2, 2, -3, 4]

    @staticmethod
    def imagine_placing_piece(imaginary_board_grid, player_number, i, j, n):
        if i < 0 or j < 0 or i >= n or j >= n or imaginary_board_grid[i][j] != -1:
            return 0
        all_turned_pieces = []
        for row_coeff in range(-1, 2):
            for column_coeff in range(-1, 2):
                k = 1
                row = i + row_coeff * k
                column = j + column_coeff * k
                turned_pieces = []
                while 0 <= row < n and 0 <= column < n and \
                        imaginary_board_grid[row][column] != -1:
                    if imaginary_board_grid[row][column] == player_number:
                        if turned_pieces:
                            all_turned_pieces.append(turned_pieces)
                        break
                    turned_pieces.append((row, column))
                    k += 1
                    row = i + row_coeff * k
                    column = j + column_coeff * k
        if not all_turned_pieces:
            return 0
        imaginary_board_grid[i][j] = player_number
        for turned_pieces in all_turned_pieces:
            for turned_piece in turned_pieces:
                imaginary_board_grid[turned_piece[0]][turned_piece[1]] = player_number
        return imaginary_board_grid

    @staticmethod
    def get_imagination_scores(board):
        scores = [0, 0]
        for row in board:
            for cell in row:
                if cell >= 0:
                    scores[cell] += 1
        return scores

    @staticmethod
    def is_imaginary_move_valid(table, n, player, i, j):
        if i < 0 or j < 0 or i >= n or j >= n or table[i][j] != -1:
            return False
        for row_coeff in range(-1, 2):
            for column_coeff in range(-1, 2):
                k = 1
                row = i + row_coeff * k
                column = j + column_coeff * k
                is_valid = False
                while 0 <= row < n and 0 <= column < n and \
                        table[row][column] != -1:
                    if table[row][column] == player:
                        if is_valid:
                            return True
                        break
                    is_valid = True
                    k += 1
                    row = i + row_coeff * k
                    column = j + column_coeff * k
        return False

    @staticmethod
    def get_actions(board, player, n):
        actions = list()
        for i in range(n):
            for j in range(n):
                if Imagination.is_imaginary_move_valid(board, n, player, i, j):
                    actions.append((i, j))
        return actions

    @staticmethod
    def heuristic(board, color):
        return Imagination.corner_weight(color, board) + Imagination.get_cost(board, color)

    @staticmethod
    def corner_weight(color, board):
        total = 0
        i = 0
        while i < 64:
            if board[i // 8][i % 8] == color:
                total += Imagination.WEIGHTS[i]
            if board[i // 8][i % 8] == -color:
                total -= Imagination.WEIGHTS[i]
            i += 1
        return total

    @staticmethod
    def get_cost(board, color):
        scores = Imagination.get_imagination_scores(board)
        num_pieces_op = scores[not color]
        num_pieces_me = scores[color]
        return num_pieces_me - num_pieces_op


class AlphaBetaPlayer(Player):
    def minmax(self):
        n = self.board.get_n()
        self.board.start_imagination()
        new_board = self.board.imaginary_board_grid
        actions = Imagination.get_actions(new_board, self.player_number, n)
        if not actions:
            score = Imagination.get_imagination_scores(new_board)
            return score, None
        best_score = -math.inf
        return_move = actions[0]
        current = new_board
        ply = 4
        for action in actions:
            new_board = current.copy()
            new_board = Imagination.imagine_placing_piece(new_board, self.player_number, action[0], action[1], n)
            score = self.min_score_alpha_beta(new_board, not self.player_number, -math.inf, math.inf, n, ply - 1)
            if score > best_score:
                best_score = score
                return_move = action
        return best_score, return_move

    def max_score_alpha_beta(self, board, color, alpha, beta, n, ply):
        if not ply:
            return Imagination.heuristic(board, color)
        best_score = -math.inf
        for action in Imagination.get_actions(board, color, n):
            new_board = board.copy()
            new_board = Imagination.imagine_placing_piece(new_board, color, action[0], action[1], n)
            score = self.min_score_alpha_beta(new_board, not color, alpha, beta, n, ply - 1)
            if score > best_score:
                best_score = score
            if best_score >= beta:
                return best_score
            alpha = max(alpha, best_score)
        return best_score

    def get_next_move(self):
        res = self.minmax()
        return res[1]

    def min_score_alpha_beta(self, board, color, alpha, beta, n, ply):
        if not ply:
            return Imagination.heuristic(board, color)
        best_score = math.inf
        for action in Imagination.get_actions(board, color, n):
            new_board = board.copy()
            new_board = Imagination.imagine_placing_piece(new_board, color, action[0], action[1], n)
            score = self.max_score_alpha_beta(new_board, not color, alpha, beta, n, ply - 1)
            if score < best_score:
                best_score = score
            if best_score <= alpha:
                return best_score
            beta = min(best_score, beta)
        return best_score
