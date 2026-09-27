import os
import itertools
from typing import Iterator, List, Optional, Dict, Any

class CandidateGenerator:
    """
    Core generator for password candidate streams.
    Supports stream processing, deduplication, and chunking.
    """

    @staticmethod
    def dictionary_attack(wordlist_paths: List[str], custom_words: Optional[List[str]] = None) -> Iterator[str]:
        seen = set()
        
        if custom_words:
            for w in custom_words:
                w_str = str(w).strip()
                if w_str and w_str not in seen:
                    seen.add(w_str)
                    yield w_str

        for path in wordlist_paths:
            if not os.path.exists(path):
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    word = line.rstrip('\r\n')
                    if word and word not in seen:
                        if len(seen) > 500000:
                            seen.clear()
                        seen.add(word)
                        yield word

    @staticmethod
    def rule_mutation_attack(base_words: List[str], rules: Dict[str, Any]) -> Iterator[str]:
        seen = set()

        substitutions = rules.get("substitutions", {"a": "@", "s": "$", "i": "1", "e": "3", "o": "0"})
        append_digits = rules.get("append_digits", True)
        prepend_digits = rules.get("prepend_digits", False)
        append_symbols = rules.get("append_symbols", ["!", "@", "#", "$", "%", "*", "_", "-"] if rules.get("append_symbols_flag") else [])
        years = rules.get("years", ["2023", "2024", "2025", "2026", "2004", "2000", "123"])

        def substitute(word: str) -> List[str]:
            res = [word]
            sub_word = word
            for char, sub in substitutions.items():
                if char in sub_word:
                    sub_word = sub_word.replace(char, sub)
            if sub_word != word:
                res.append(sub_word)
            return res

        for word in base_words:
            if not word:
                continue

            variants = {
                word,
                word.lower(),
                word.upper(),
                word.capitalize(),
                word[::-1]
            }

            for v in list(variants):
                for sub_v in substitute(v):
                    variants.add(sub_v)

            for v in list(variants):
                if v not in seen:
                    seen.add(v)
                    yield v

                for yr in years:
                    c1 = f"{v}{yr}"
                    c2 = f"{yr}{v}"
                    if c1 not in seen:
                        seen.add(c1); yield c1
                    if c2 not in seen:
                        seen.add(c2); yield c2

                if append_digits:
                    for d in range(10):
                        c = f"{v}{d}"
                        if c not in seen:
                            seen.add(c); yield c
                if prepend_digits:
                    for d in range(10):
                        c = f"{d}{v}"
                        if c not in seen:
                            seen.add(c); yield c

                for sym in append_symbols:
                    c = f"{v}{sym}"
                    if c not in seen:
                        seen.add(c); yield c
                    for yr in years:
                        c_sym_yr = f"{v}{sym}{yr}"
                        if c_sym_yr not in seen:
                            seen.add(c_sym_yr); yield c_sym_yr

    @staticmethod
    def mask_attack(mask: str, custom_charsets: Optional[Dict[str, str]] = None) -> Iterator[str]:
        CHARSETS = {
            "?l": "abcdefghijklmnopqrstuvwxyz",
            "?u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "?d": "0123456789",
            "?s": "!@#$%^&*()_+-=",
            "?a": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-="
        }
        if custom_charsets:
            CHARSETS.update(custom_charsets)

        i = 0
        pattern_sets = []
        while i < len(mask):
            if mask[i] == '?' and i + 1 < len(mask):
                token = mask[i:i+2]
                if token in CHARSETS:
                    pattern_sets.append(list(CHARSETS[token]))
                    i += 2
                    continue
            pattern_sets.append([mask[i]])
            i += 1

        for combo in itertools.product(*pattern_sets):
            yield "".join(combo)

    @staticmethod
    def hybrid_attack(base_words: List[str], prefixes: List[str], suffixes: List[str], add_years: bool = True, add_symbols: bool = True) -> Iterator[str]:
        seen = set()
        years = ["2000", "2004", "2020", "2021", "2022", "2023", "2024", "2025", "2026"] if add_years else [""]
        symbols = ["", "@", "!", "_", "#", "$"] if add_symbols else [""]
        
        pref_list = prefixes if prefixes else [""]
        suff_list = suffixes if suffixes else [""]

        for w in base_words:
            for p in pref_list:
                for s in suff_list:
                    for yr in years:
                        for sym in symbols:
                            c1 = f"{p}{w}{s}{sym}{yr}"
                            c2 = f"{p}{w}{yr}{sym}{s}"
                            for cand in (c1, c2):
                                if cand and cand not in seen:
                                    seen.add(cand)
                                    yield cand

    @staticmethod
    def brute_force_attack(charset: str, min_len: int, max_len: int, prefixes: Optional[List[str]] = None, suffixes: Optional[List[str]] = None) -> Iterator[str]:
        pref_list = prefixes if prefixes else [""]
        suff_list = suffixes if suffixes else [""]
        for p in pref_list:
            for s in suff_list:
                for length in range(min_len, max_len + 1):
                    for combo in itertools.product(charset, repeat=length):
                        yield f"{p}{''.join(combo)}{s}"

    @staticmethod
    def calculate_mask_space(mask: str, custom_charsets: Optional[Dict[str, str]] = None) -> int:
        CHARSETS = {
            "?l": "abcdefghijklmnopqrstuvwxyz",
            "?u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "?d": "0123456789",
            "?s": "!@#$%^&*()_+-=",
            "?a": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-="
        }
        if custom_charsets:
            CHARSETS.update(custom_charsets)

        i = 0
        total = 1
        while i < len(mask):
            if mask[i] == '?' and i + 1 < len(mask):
                token = mask[i:i+2]
                if token in CHARSETS:
                    total *= len(CHARSETS[token])
                    i += 2
                    continue
            total *= 1
            i += 1
        return total

    @staticmethod
    def calculate_brute_force_space(charset_len: int, min_len: int, max_len: int, prefixes: Optional[List[str]] = None, suffixes: Optional[List[str]] = None) -> int:
        total_combos = sum(charset_len ** l for l in range(min_len, max_len + 1))
        pref_count = len(prefixes) if prefixes else 1
        suff_count = len(suffixes) if suffixes else 1
        return total_combos * pref_count * suff_count
