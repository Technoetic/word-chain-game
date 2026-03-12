"""Prompt builder for LLM-based word chain game."""


class PromptBuilder:
    """Builds system and user prompts for Claude in word chain game."""

    @staticmethod
    def build_system(difficulty: str = "normal", revenge: bool = False) -> str:
        base_prompt = """너는 한국어 끝말잇기 AI 플레이어다.

규칙:
- 주어진 글자로 시작하는 한국어 명사만 답한다
- 2글자 이상의 단어만 가능
- 이전에 사용된 단어는 사용 불가
- 국어사전에 있는 정확한 명사만 답한다

두음법칙:
- 녀→여, 뇨→요, 뉴→유, 니→이, 랴→야, 려→여, 례→예, 료→요, 류→유, 리→이, 라→나, 래→내, 로→노, 뢰→뇌, 루→누, 르→느

응답: 단어 하나만. 설명/문장 금지.
"""

        if revenge:
            base_prompt += (
                "\n전략: 상대에게 복수한다. 끝 글자가 '럽', '릎', '듐', '륨', '늄', "
                "'뀨', '쀼', '튐' 등 이을 수 없는 글자(한방 글자)로 끝나는 단어를 "
                "최우선으로 선택해라. 예: 칼슘, 나트륨, 무릎, 사랑스럽→X(형용사), "
                "스튜디움, 알루미늄, 플루토늄 등.\n"
            )

        if difficulty == "easy":
            base_prompt += "\n난이도: 쉬움 (일반적인 단어)"
        elif difficulty == "hard":
            base_prompt += "\n난이도: 어려움 (창의적이고 어려운 단어, 한방 글자 적극 활용)"
        else:
            base_prompt += "\n난이도: 중간"

        return base_prompt

    @staticmethod
    def build_user(
        target_char: str, used_words: list[str], difficulty: str = "normal"
    ) -> str:
        prompt = f"'{target_char}'로 시작하는 2글자 이상 한국어 명사 하나만 답해."

        if used_words:
            recent = used_words[-20:]  # only send last 20 to save tokens
            prompt += f"\n\n사용된 단어: {', '.join(recent)}"
            prompt += "\n위 단어들은 사용 불가."

        return prompt
