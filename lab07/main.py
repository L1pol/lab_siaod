from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab_results import save_results

import argparse
import random
import statistics
import time


def suffix_shifts(pattern):
    m = len(pattern)
    shifts = [0] * (m + 1)
    borders = [0] * (m + 1)
    i, j = m, m + 1
    borders[i] = j
    while i:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            if not shifts[j]:
                shifts[j] = j - i
            j = borders[j]
        i -= 1
        j -= 1
        borders[i] = j
    j = borders[0]
    for i in range(m + 1):
        if not shifts[i]:
            shifts[i] = j
        if i == j:
            j = borders[j]
    return shifts


def naive_search(text: str, pattern: str) -> tuple[list[int], int]:
    hits = []
    count = 0
    if pattern:
        for start in range(len(text) - len(pattern) + 1):
            for j, char in enumerate(pattern):
                count += 1
                if text[start + j] != char:
                    break
            else:
                hits.append(start)
    return hits, count


def prefix_function(pattern: str) -> list[int]:
    pi = [0] * len(pattern)
    for i in range(1, len(pattern)):
        j = pi[i - 1]
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        pi[i] = j
    return pi


def kmp_search(text: str, pattern: str) -> tuple[list[int], int]:
    if not pattern:
        return [], 0
    pi = prefix_function(pattern)
    hits = []
    j = count = 0
    for i, char in enumerate(text):
        while True:
            count += 1
            if char == pattern[j]:
                j += 1
                break
            if not j:
                break
            j = pi[j - 1]
        if j == len(pattern):
            hits.append(i - j + 1)
            j = pi[j - 1]
    return hits, count


def rabin_karp_search(text: str, pattern: str,
                      base: int = 256, mod: int = 1_000_000_007) -> tuple[list[int], int]:
    m = len(pattern)
    if not m or m > len(text):
        return [], 0
    target = window = count = 0
    for i in range(m):
        target = (target * base + ord(pattern[i])) % mod
        window = (window * base + ord(text[i])) % mod
    power = pow(base, m - 1, mod)
    hits = []
    for i in range(len(text) - m + 1):
        if target == window:
            for j in range(m):
                count += 1
                if pattern[j] != text[i + j]:
                    break
            else:
                hits.append(i)
        if i + m < len(text):
            window = ((window - ord(text[i]) * power) * base + ord(text[i + m])) % mod
    return hits, count


def bad_char_table(pattern: str) -> dict[str, int]:
    return {char: i for i, char in enumerate(pattern)}


def boyer_moore_search(text: str, pattern: str) -> tuple[list[int], int]:
    m = len(pattern)
    if not m:
        return [], 0
    last = bad_char_table(pattern)
    shift = suffix_shifts(pattern)
    hits = []
    start = count = 0
    while start <= len(text) - m:
        j = m - 1
        while j >= 0:
            count += 1
            if pattern[j] != text[start + j]:
                break
            j -= 1
        if j < 0:
            hits.append(start)
            start += shift[0]
        else:
            start += max(shift[j + 1], j - last.get(text[start + j], -1))
    return hits, count


def reference_occurrences(text: str, pattern: str) -> list[int]:
    if not pattern:
        return []
    result = []
    pos = text.find(pattern)
    while pos != -1:
        result.append(pos)
        pos = text.find(pattern, pos + 1)
    return result


def self_check() -> None:
    assert reference_occurrences("aaaa", "aa") == [0, 1, 2]
    assert reference_occurrences("abc", "abcd") == []

    assert prefix_function("abcabcd") == [0, 0, 0, 1, 2, 3, 0]
    assert prefix_function("aabaaab") == [0, 1, 0, 1, 2, 2, 3]

    algorithms = [naive_search, kmp_search, rabin_karp_search, boyer_moore_search]
    for search in algorithms:
        name = search.__name__
        occ, _ = search("aaaa", "aa")
        assert occ == [0, 1, 2], f"{name}: перекрывающиеся вхождения теряются"
        occ, _ = search("abc", "abc")
        assert occ == [0], f"{name}: шаблон, равный тексту"
        occ, _ = search("abc", "abcd")
        assert occ == [], f"{name}: шаблон длиннее текста"
        occ, _ = search("", "a")
        assert occ == [], f"{name}: пустой текст"
        occ, _ = search("abc", "")
        assert occ == [], f"{name}: пустой шаблон (инвариант заготовки)"

    rng = random.Random(0)
    for _ in range(300):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(1, 60)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        expected = reference_occurrences(text, pattern)
        for search in algorithms:
            occ, comparisons = search(text, pattern)
            assert occ == expected, (
                f"{search.__name__}: text={text!r}, pattern={pattern!r}, "
                f"получено {occ}, ожидалось {expected}"
            )
            assert comparisons >= 0
    print("self_check: OK")


TEXT_SIZE = 100_000
PATTERN_LENGTHS = [4, 16, 64]
REPEATS = 5


def bench(search, text: str, pattern: str) -> float:
    search(text, pattern)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        search(text, pattern)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed):
    from tempfile import TemporaryDirectory
    from scripts.generate_data import generate_texts

    rng = random.Random(seed)
    rows = []
    with TemporaryDirectory() as directory:
        folder = Path(directory)
        generate_texts(folder, seed, length=TEXT_SIZE)
        for group in ("small_alphabet", "natural"):
            text = (folder / f"texts_{group}.txt").read_text(encoding="utf8").rstrip("\n")
            for length in PATTERN_LENGTHS:
                start = rng.randrange(len(text) - length + 1)
                pattern = text[start:start + length]
                expected = reference_occurrences(text, pattern)
                for fn in (naive_search, kmp_search, rabin_karp_search, boyer_moore_search):
                    hits, count = fn(text, pattern)
                    if hits != expected:
                        raise ValueError(fn.__name__)
                    rows.append((group, fn.__name__, length, bench(fn, text, pattern), count, len(hits)))
    save_results(__file__, ("Текст", "Поиск", "Длина шаблона", "Время, с", "Сравнения", "Вхождения"), rows, metrics=(3, 4))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    if rabin_karp_search("baab", "ab", mod=1)[0] != [2]:
        raise ValueError("Ложное совпадение при коллизии")
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
