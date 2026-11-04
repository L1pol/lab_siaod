from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab_results import save_results
from lab03.main import quick_sort as lab03_quick_sort

import argparse
import random
import statistics
import time
import traceback


def stable_pass(values, width, key):
    counts = [0] * width
    for value in values:
        digit = key(value)
        if not 0 <= digit < width:
            raise ValueError("Ключ вне диапазона")
        counts[digit] += 1
    for i in range(1, width):
        counts[i] += counts[i - 1]
    result = [None] * len(values)
    for value in reversed(values):
        digit = key(value)
        counts[digit] -= 1
        result[counts[digit]] = value
    return result


def merge(left: list, right: list, key) -> list:
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def merge_sort(a: list, key=lambda x: x) -> list:
    if len(a) < 2:
        return a.copy()
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    return stable_pass(a, key_max + 1, lambda value: value)


def radix_sort_lsd(a: list[int]) -> list[int]:
    if any(x < 0 for x in a):
        raise ValueError("Нужны неотрицательные ключи")
    out = a.copy()
    maximum = max(a, default=0)
    exp = 1
    while exp <= maximum:
        out = stable_pass(out, 10, lambda x: (x // exp) % 10)
        exp *= 10
    return out


def sift_down(a: list[int], i: int, n: int) -> None:
    while 2 * i + 1 < n:
        child = 2 * i + 1
        if child + 1 < n and a[child] < a[child + 1]:
            child += 1
        if a[i] >= a[child]:
            break
        a[i], a[child] = a[child], a[i]
        i = child


def heap_sort(a: list[int]) -> None:
    for i in range(len(a) // 2 - 1, -1, -1):
        sift_down(a, i, len(a))
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def quick_sort(a: list[int]) -> list[int]:
    return lab03_quick_sort(a, random)


class SelfCheckError(Exception):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    buf = list(a)
    heap_sort(buf)
    return buf


SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    boundary = [
        [],
        [7],
        [0],
        [5, 5, 5],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")


def self_check() -> None:
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")

    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100
WIDE_KEY_MAX = 10**9


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    almost = list(range(n))
    for _ in range(max(1, n // 100)):
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    fn(list(data))
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed):
    rng = random.Random(seed)
    rows = []
    for n in SIZES:
        for group, data in make_datasets(rng, n).items():
            for name, fn in [*SORTS.items(), ("sorted", sorted)]:
                if name == "counting_sort":
                    if group == "random_wide":
                        continue
                    fn = lambda a: counting_sort(a, max(a, default=0))
                if name == "heap_sort":
                    fn = heap_sort
                rows.append((group, name, n, bench(fn, data)))
    save_results(__file__, ("Вход", "Алгоритм", "n", "Время, с"), rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    pairs = [(2, "A"), (1, "B"), (2, "C")]
    expect(stable_pass(pairs, 3, lambda p: p[0]) == [pairs[1], pairs[0], pairs[2]], "устойчивость подсчёта")
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
