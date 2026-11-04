from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab_results import save_results

import argparse
import bisect
import random
import statistics
import time


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    for i, value in enumerate(a):
        if value == key:
            return i, i + 1
    return -1, len(a)


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    lo, hi = 0, len(a) - 1
    count = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        count += 1
        if a[mid] == key:
            return mid, count
        count += 1
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, count


def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    lo, hi = 0, len(a) - 1
    count = 0
    while lo <= hi:
        count += 1
        if key < a[lo]:
            break
        count += 1
        if key > a[hi]:
            break
        if a[hi] == a[lo]:
            return lo, count
        pos = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        count += 1
        if key == a[pos]:
            return pos, count
        count += 1
        if a[pos] < key:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1, count


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]


def self_check() -> None:
    for name, fn in ALGORITHMS:
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"

        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"

        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона"

    rng = random.Random(0)
    for _ in range(300):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)

        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"

        if present:
            assert linear_search(a, key)[0] == a.index(key)
    print("self_check: OK")


SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
N_KEYS = 40


def bench(fn, a: list[int], keys: list[int]) -> float:
    for k in keys:
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    return statistics.mean(fn(a, k)[1] for k in keys)


def run_benchmarks(seed):
    rng = random.Random(seed)
    rows = []
    for dist in ("uniform", "exponential"):
        for n in SIZES:
            data = make_dataset(n, dist, rng)
            for present in (True, False):
                keys = pick_keys(data, rng, N_KEYS, present)
                group = dist + (" / есть" if present else " / нет")
                for name, fn in ALGORITHMS:
                    duration = bench(fn, data, keys) / len(keys) * 1e6
                    rows.append((group, name, n, duration, mean_comparisons(fn, data, keys)))
    save_results(__file__, ("Вход", "Поиск", "n", "Время, мкс", "Сравнений на запрос"), rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
