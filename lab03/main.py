from pathlib import Path
import argparse
import csv
import random
import statistics
from time import perf_counter
from dataclasses import dataclass, field

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def bubble_sort(data):
    a = data.copy()
    comparisons = swaps = 0
    for end in range(len(a) - 1, 0, -1):
        changed = False
        for i in range(end):
            comparisons += 1
            if a[i + 1] < a[i]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swaps += 1
                changed = True
        if not changed:
            break
    return a, comparisons, swaps


def insertion_sort(data):
    a = data.copy()
    comparisons = shifts = 0
    for i in range(1, len(a)):
        value = a[i]
        j = i
        while j > 0:
            comparisons += 1
            if not value < a[j - 1]:
                break
            a[j] = a[j - 1]
            shifts += 1
            j -= 1
        a[j] = value
    return a, comparisons, shifts


def selection_sort(data):
    a = data.copy()
    comparisons = swaps = 0
    for i in range(len(a) - 1):
        best = i
        for j in range(i + 1, len(a)):
            comparisons += 1
            if a[j] < a[best]:
                best = j
        if i != best:
            a[i], a[best] = a[best], a[i]
            swaps += 1
    return a, comparisons, swaps


def quick_sort(data, rng=None):
    rng = rng if rng is not None else random.Random()
    a = data.copy()

    def sort(lo, hi):
        while hi - lo > 1:
            pivot = a[rng.randrange(lo, hi)]
            left = i = lo
            right = hi
            while i < right:
                if a[i] < pivot:
                    a[left], a[i] = a[i], a[left]
                    left += 1
                    i += 1
                elif pivot < a[i]:
                    right -= 1
                    a[i], a[right] = a[right], a[i]
                else:
                    i += 1
            if left - lo < hi - right:
                sort(lo, left)
                lo = right
            else:
                sort(right, hi)
                hi = left

    sort(0, len(a))
    return a


SIMPLE = (bubble_sort, insertion_sort, selection_sort)
ALGORITHMS = (*SIMPLE, quick_sort)


@dataclass(order=True)
class Item:
    key: int
    label: str = field(compare=False)


def run(fn, data, seed):
    if fn is quick_sort:
        return quick_sort(data, random.Random(seed)), None, None
    return fn(data)


def self_check(seed):
    rng = random.Random(seed)
    cases = [[], [1], [4] * 10, list(range(9)), list(range(9, -1, -1))]
    cases.extend([rng.randrange(-10, 11) for _ in range(rng.randrange(81))]
                 for _ in range(300))
    pairs = [Item(2, "A"), Item(2, "B"), Item(1, "C")]
    for fn in ALGORITHMS:
        for data in cases:
            original = data.copy()
            result, _, _ = run(fn, data, seed)
            if data != original or result != sorted(original):
                raise ValueError((fn.__name__, original, result))
        result, _, _ = run(fn, pairs, seed)
        labels = "".join(item.label for item in result)
        print(fn.__name__, labels)
        expected = "CAB" if fn in (bubble_sort, insertion_sort) else "CBA"
        if labels != expected and (fn is not quick_sort or seed == 37):
            raise ValueError((fn.__name__, labels))
    for n in range(2, 20):
        ordered = list(range(n))
        reverse = ordered[::-1]
        total = n * (n - 1) // 2
        for fn in SIMPLE:
            if fn(ordered)[1:] != (total if fn is selection_sort else n - 1, 0):
                raise ValueError(fn.__name__)
            if fn(reverse)[1:] != (total, n // 2 if fn is selection_sort else total):
                raise ValueError(fn.__name__)


def benchmark(seed, out):
    out.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    classes = ("По возрастанию", "Случайный", "По убыванию")
    with (out / "results.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        table = csv.writer(stream)
        table.writerow(("algorithm", "input", "n", "median_seconds", "comparisons", "swaps_or_shifts"))
        for fn in ALGORITHMS:
            sizes = (1000, 3000, 10000, 30000, 100000) if fn is quick_sort else (128, 256, 512, 1024, 2048)
            times = [[] for _ in classes]
            for n in sizes:
                rng = random.Random(seed + n)
                data = [rng.randint(-1000000, 1000000) for _ in range(n)]
                for k, values in enumerate((sorted(data), data, sorted(data, reverse=True))):
                    result, comparisons, moves = run(fn, values, seed)
                    if result != sorted(values):
                        raise ValueError(fn.__name__)
                    samples = []
                    for _ in range(5):
                        start = perf_counter()
                        run(fn, values, seed)
                        samples.append(perf_counter() - start)
                    median = statistics.median(samples)
                    table.writerow((fn.__name__, classes[k], n, median, comparisons, moves))
                    times[k].append(median)
            for ax, values in zip(axes, times):
                slope = np.polyfit(np.log(sizes), np.log(values), 1)[0]
                print(fn.__name__, ax.get_label(), round(slope, 2))
                ax.loglog(sizes, values, "o-", label=f"{fn.__name__} ({slope:.2f})")
    for ax, title in zip(axes, classes):
        ax.set(title=title, xlabel="Число элементов", ylabel="Медиана времени, с")
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=8)
    fig.savefig(out / "timings.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    seed = 30 + args.variant
    self_check(seed)
    if not args.check_only:
        benchmark(seed, args.out)
