class bullscows:

    def __init__(self, seq_len=4, alpha_size=9):
        """seq_len - length of sequence
           alpha_size - size of alphabet (number of first characters from 1-9,0,A-Z)"""
        max_alphabet = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if seq_len < 2:
            raise ValueError("sequence length must be at least 2")
        elif seq_len > alpha_size:
            raise ValueError("sequence length must not be more than alphabet size")
        elif alpha_size > len(max_alphabet):
            raise ValueError("the longest alphabet supported is 1-9 + 0 + A-Z (36 characters)")
        self.seq_len = seq_len
        self.alpha_size = alpha_size
        self.alphabet = max_alphabet[:alpha_size]
        self.n_operations = None
        self.n_moves = None
        self.time_elapsed = None
        self.last_guess = None

    def _get_bc(self, guess, ans):
        """returns (b, c) if guess has b bulls and c cows regarding ans as the right answer"""
        if len(guess) != len(ans):
            raise ValueError("invalid sequence")
        elif len(set(guess)) != len(guess):
            raise ValueError("invalid sequence")
        n_bulls = 0
        n_cows = 0
        for c1, c2 in zip(guess, ans):
            if c1 == c2:
                n_bulls += 1
            elif c1 in ans:
                n_cows += 1
        return n_bulls, n_cows

    @staticmethod
    def _comb_perm(iterable, r):
        """like combinations from itertools, but order-sensitive"""
        from itertools import combinations, permutations
        for comb in combinations(iterable, r):
            yield from permutations(comb)

    def _gen_cands(self, guess, response):
        """generate all sequences such that _get_bc(sequence, guess) == response"""
        if len(guess) != self.seq_len:
            raise ValueError()
        from itertools import combinations, permutations
        n_bulls, n_cows = response
        cand = ['-'] * self.seq_len
        for bull_idx in combinations(range(self.seq_len), n_bulls) if n_bulls else [[]]:
            for bull_i in bull_idx:
                cand[bull_i] = guess[bull_i]
            non_bull_idx = sorted(set(range(self.seq_len)) - set(bull_idx))
            for cow_choice in combinations(range(self.seq_len - n_bulls), n_cows) if n_cows else [[]]:
                for perm in bullscows._comb_perm(range(self.seq_len - n_bulls), n_cows) if n_cows else [[]]:
                    for p, c in zip(perm, cow_choice):
                        if p == c:
                            break
                        cand[non_bull_idx[p]] = guess[non_bull_idx[c]]
                    else:
                        cow_idx = sorted(non_bull_idx[i] for i in perm)
                        nonbc_idx = sorted(set(range(self.seq_len)) - set(bull_idx) - set(cow_idx))
                        nonbc = list(set(self.alphabet) - set(guess))
                        n_rest = len(nonbc_idx)
                        for rest in bullscows._comb_perm(nonbc, n_rest):
                            for i, c in zip(nonbc_idx, rest):
                                cand[i] = c
                            yield ''.join(cand)

    def _gen_all_seq(self):
        """generate all sequences for current seq_len, alpha_size configuration"""
        from itertools import permutations, combinations
        yield from (''.join(self.alphabet[i] for i in guess)
            for guess in bullscows._comb_perm(range(self.alpha_size), self.seq_len)
        )

    def _gen_seq(self):
        """generate random sequence"""
        from random import sample
        return ''.join(sample(self.alphabet, self.seq_len))

    @staticmethod
    def _seq_cnt(alpha_size, seq_len):
        """calculate how many sequences are if specified (alpha_size, seq_len) configuration"""
        from operator import mul
        from functools import reduce
        return reduce(mul, range(alpha_size - seq_len + 1, alpha_size + 1))

    def _solve(self, ans_func):
        """ans_func(guess) -> (b, c) for guess regarding the right answer"""
        from random import choice
        from datetime import datetime
        from random import random
        t1 = datetime.now()
        i = 1
        n_operations = 0
        move = self._gen_seq()
        response = ans_func(move)
        if response[0] != self.seq_len:
            yield None
            cands = list(self._gen_cands(move, response))
            n_operations += bullscows._seq_cnt(self.alpha_size, self.seq_len)
            i += 1
            while True:
                if not cands:
                    raise EOFError("There are mistakes in given information. Cancelling the game.")
                if i == 2 \
                    and self.last_guess is not None \
                    and self._get_bc(move, self.last_guess) == response \
                    and random() <= 0.4:
                    move = self.last_guess
                else:
                    move = choice(cands)
                response = ans_func(move)
                if response[0] == self.seq_len:
                    break
                yield None
                n_operations += len(cands)
                cands = [cand for cand in cands if self._get_bc(cand, move) == response]
                i += 1
        t2 = datetime.now()
        self.time_elapsed = (t2 - t1).total_seconds()
        self.n_moves = i
        self.n_operations = n_operations
        self.last_guess = move
        yield move

    def two_side_play(self):
        """play in current configuration.
        you guess computer's number while it guesses yours"""
        from time import sleep
        def get_response(move):
            while True:
                print(f"is it {move} ? ", end='')
                ans = input()
                if ans and ans.lower().strip()[0] == 'q':
                    raise EOFError()
                if ans and ans.lower().strip()[0] == 'y':
                    b, c = self.seq_len, 0
                    break
                spl = ans.split()
                if len(spl) != 2:
                    print("error: invalid format. try writing again")
                    continue
                try:
                    b, c = int(spl[0]), int(spl[1])
                except Exception as e:
                    print("error: invalid format. try writing again")
                    continue
                if b < 0 or c < 0 or b + c > self.seq_len or b + c == self.seq_len and c == 1:
                    print("error: invalid bulls/cows number. try writing again")
                    continue
                break
            return b, c

        ai_solution = self._gen_seq()
        def type_move():
            while True:
                s = "your move: "
                print(f"{s:>50}", end='')
                move = input().upper().strip()
                if move == 'Q':
                    raise EOFError()
                if len(move) != self.seq_len or not (set(move) < set(self.alphabet)):
                    s = "error: invalid format. try writing again"
                    print(f"{s:>60}")
                    continue
                try:
                    b, c = self._get_bc(move, ai_solution)
                    break
                except:
                    s = "error. try writing again"
                    print(f"{s:>60}")
                    continue
            if (b, c) == (self.seq_len, 0):
                s = "yes, it is my number"
                print(f"{s:>60}")
                return True
            else:
                s = f"{b} b, {c} c in {move}"
                print(f"{s:>60}")
                return False

        print("press Enter when you make up your number...", end='')
        input()
        try:
            solve_gen = self._solve(get_response)
            y = None
            n_player_moves = 0
            game_result_msg = None
            player_guessed = type_move()
            ai_guessed = False
            n_player_moves += 1
            if player_guessed:
                s = f"You've guessed it in {n_player_moves} moves"
                print(f"{s:>60}")
            for y in solve_gen:
                if y is not None:
                    ai_guessed = True
                    print(f"AI guessed it in {self.n_moves} moves")
                if not player_guessed:
                    if ai_guessed and self.n_moves == n_player_moves:
                        if game_result_msg is not None:
                            print("(error in game result msg)")
                        game_result_msg = "YOU LOSE"
                        print(f"{game_result_msg:^60}")
                    player_guessed = type_move()
                    n_player_moves += 1
                    if player_guessed:
                        s = f"You've guessed it in {n_player_moves} moves"
                        print(f"{s:>60}")
                elif self.n_moves == n_player_moves:
                    if game_result_msg is not None:
                        print("(error in game result msg)")
                    game_result_msg = "YOU WIN" if not ai_guessed else "DRAW"
                    print(f"{game_result_msg:^60}")
            while not player_guessed:
                player_guessed = type_move()
                n_player_moves += 1
                if player_guessed:
                    s = f"You've guessed it in {n_player_moves} moves"
                    print(f"{s:>60}")
            s = "SUMMARY:"
            sleep(1)
            print(f"{s:^60}")
            print(f"AI moves: {self.n_moves}")
            s = f"player moves: {n_player_moves}"
            print(f"{s:>60}")
            print(f"{game_result_msg:^60}"
                if game_result_msg is not None
                else "(error in game result msg)"
            )
        except EOFError as e:
            print(e)
            s = "STOPPING THE GAME"
            print(f"{s:^60}")
            if game_result_msg is not None:
                s = "anyway, " + game_result_msg
                print(f"{s:^60}")
        except Exception as e:
            raise

if __name__ == "__main__":
    try:
        bc = bullscows()
        print(f"configuration is:\n{bc.seq_len}-digit sequences of numbers from ({bc.alphabet}).\nuse this one? (y / n)")
        ans = input()
        if ans and ans.lower().strip()[0] != "y":
            while True:
                print("number of possible digits:")
                ans1 = input()
                print("length of sequence (number):")
                ans2 = input()
                try:
                    bc = bullscows(int(ans2.strip()), int(ans1.strip()))
                    print(f"configuration is:\n{bc.seq_len}-digit sequences of numbers from ({bc.alphabet})")
                    break
                except:
                    print("error: invalid parameters. try other")
                    continue
        print(
    """\twhen saying how many BULLS and COWS,
\ttype ONLY numbers divided by spaces*
\t*except \"y\" if computer guessed your number
\tand \"q\" to stop the game""")
        while True:
            print("-" * 60)
            bc.two_side_play()
            s = "TRY AGAIN? (y / n)"
            print(f"{s:^60}")
            ans = input()
            if ans and ans.lower().strip()[0] != "y":
                break
    except KeyboardInterrupt:
        print("\nForce quit...")
