#!/usr/bin/env python3
"""Utility functions for natural language processing."""

from tiktoken import encoding_for_model

class Encoder:
    def __init__(self):
        self.encoder = encoding_for_model("gpt-4")

    def get_num_tokens(self, text=""):
        return len(self.get_tokens(text))

    def get_tokens(self, text=""):
        return self.encoder.encode(text)

    def get_text_from_tokens(self, tokens):
        return self.encoder.decode(tokens)

    def truncate_text(self, company_text_data, param):
        return self.get_text_from_tokens(self.get_tokens(company_text_data)[:param])