from .base_gpt import BaseGPT


class GPT4o(BaseGPT):
    def __init__(self) -> None:
        super().__init__("gpt-4o")