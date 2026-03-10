class ScoringSystem:
    BASE_SCORE = 100
    KILLER_BONUS = 500

    def calculate(self, word: str, combo: int, time_left: int = 15) -> int:
        detail = self.calculate_detail(word, combo, time_left)
        return detail["total"]

    def calculate_detail(self, word: str, combo: int, time_left: int = 15) -> dict:
        if not word:
            return {"total": 0, "base": 0, "combo_mult": 1.0, "time_bonus": 0, "killer_bonus": 0}

        base = self.BASE_SCORE + (len(word) - 2) * 10
        combo_mult = self.get_combo_multiplier(combo)
        time_ratio = max(0, time_left) / 15.0
        before_killer = int(base * combo_mult * (1 + time_ratio * 0.1))
        time_bonus_val = before_killer - int(base * combo_mult)
        killer = self.KILLER_BONUS if self.is_killer_word(word) else 0
        total = before_killer + killer

        return {
            "total": total,
            "base": base,
            "combo_mult": combo_mult,
            "time_bonus": time_bonus_val,
            "killer_bonus": killer,
            "length": len(word),
        }

    def get_combo_multiplier(self, combo: int) -> float:
        if combo <= 0:
            return 1.0
        elif combo == 1:
            return 1.5
        elif combo == 2:
            return 2.0
        elif combo == 3:
            return 2.5
        else:
            return 3.0

    def is_killer_word(self, word: str) -> bool:
        if not word:
            return False

        last_char = word[-1]
        code = ord(last_char)
        if 0xAC00 <= code <= 0xD7A3:
            final_index = (code - 0xAC00) % 28
            rare_finals = {3, 5, 6, 9, 10, 11, 12, 13, 14, 15, 18, 20}
            return final_index in rare_finals
        return False
