from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab_results import save_results

import argparse
import random
import statistics
import string
import time


P = 31


def poly_hash(key: str, mod: int) -> int:
    h = 0
    for char in key:
        h = (h * P + ord(char)) % mod
    return h


def bad_hash(key: str, mod: int) -> int:
    return (ord(key[0]) if key else 0) % mod


class HashTable:
    INITIAL_CAPACITY = 8

    def __init__(self, capacity: int = INITIAL_CAPACITY, hash_fn=poly_hash,
                 max_load_factor: float = 0.75) -> None:
        self._buckets: list[list[tuple[str, object]]] = [[] for _ in range(capacity)]
        self._size = 0
        self._hash_fn = hash_fn

        self._max_load_factor = max_load_factor

    def _bucket_index(self, key: str) -> int:
        return self._hash_fn(key, len(self._buckets))

    @property
    def load_factor(self) -> float:
        return self._size / len(self._buckets)

    def put(self, key: str, value: object) -> None:
        bucket = self._buckets[self._bucket_index(key)]
        for i, (existing, _) in enumerate(bucket):
            if existing == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1
        if self.load_factor > self._max_load_factor:
            self._rehash()

    def get(self, key: str, default: object = None) -> object:
        for existing, value in self._buckets[self._bucket_index(key)]:
            if existing == key:
                return value
        return default

    def delete(self, key: str) -> None:
        bucket = self._buckets[self._bucket_index(key)]
        for i, (existing, _) in enumerate(bucket):
            if existing == key:
                bucket.pop(i)
                self._size -= 1
                return
        raise KeyError(key)

    def __len__(self) -> int:
        return self._size

    def _rehash(self) -> None:
        old = self._buckets
        self._buckets = [[] for _ in range(2 * len(old))]
        for bucket in old:
            for key, value in bucket:
                self._buckets[self._bucket_index(key)].append((key, value))

    def chain_lengths(self) -> list[int]:
        return [len(bucket) for bucket in self._buckets]


def check_invariants(table: HashTable) -> None:
    n_buckets = len(table._buckets)
    seen: set[str] = set()
    for i, bucket in enumerate(table._buckets):
        for key, _value in bucket:
            assert table._hash_fn(key, n_buckets) == i, \
                f"ключ {key!r} лежит не в своём бакете"
            assert key not in seen, f"ключ {key!r} встречается дважды"
            seen.add(key)
    assert sum(table.chain_lengths()) == len(table), \
        "сумма длин цепочек не равна размеру таблицы"


def random_keys(rng: random.Random, n: int, length: int = 8) -> list[str]:
    keys: set[str] = set()
    while len(keys) < n:
        keys.add("".join(rng.choice(string.ascii_lowercase) for _ in range(length)))
    return sorted(keys)


def self_check(seed=37) -> None:
    t = HashTable()
    assert len(t) == 0
    assert t.get("нет") is None
    t.put("a", 1)
    t.put("a", 2)
    assert len(t) == 1 and t.get("a") == 2
    t.delete("a")
    assert len(t) == 0
    try:
        t.delete("a")
        raise AssertionError("delete отсутствующего ключа обязан дать KeyError")
    except KeyError:
        pass

    t = HashTable()
    rng = random.Random(seed)
    for key in random_keys(rng, 100):
        t.put(key, 0)
    assert len(t) == 100 and t.load_factor <= t._max_load_factor
    check_invariants(t)

    t, etalon = HashTable(), {}
    keys = random_keys(rng, 40)
    for _ in range(2000):
        key, op = rng.choice(keys), rng.random()
        if op < 0.5:
            value = rng.randint(0, 999)
            t.put(key, value)
            etalon[key] = value
        elif op < 0.8:
            assert t.get(key, -1) == etalon.get(key, -1)
        elif key in etalon:
            t.delete(key)
            del etalon[key]
        assert len(t) == len(etalon)
    check_invariants(t)
    print("self_check: OK")


ALPHAS = [0.1, 0.25, 0.5, 0.75, 1.0, 2.0]
CAPACITY = 4096
N_PROBES = 1000
REPEATS = 5


def bench(fn) -> float:
    fn()
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed):
    rng = random.Random(seed)
    keys = random_keys(rng, 2000)
    histogram = []
    for name, fn in (("Полиномиальная", poly_hash), ("Первый символ", bad_hash)):
        table = HashTable(512, fn, float("inf"))
        for key in keys:
            table.put(key, 0)
        lengths = table.chain_lengths()
        for length in sorted(set(lengths)):
            histogram.append(("Распределение цепочек", name, length, lengths.count(length)))
    save_results(__file__, ("Набор", "Хеш", "Длина цепочки", "Число бакетов"), histogram, stem="chains", bars=True)
    rows = []
    for alpha in ALPHAS:
        table = HashTable(CAPACITY, max_load_factor=float("inf"))
        keys = random_keys(rng, int(CAPACITY * alpha))
        ref = dict.fromkeys(keys, 0)
        for key in keys:
            table.put(key, 0)
        probes = rng.choices(keys, k=N_PROBES)
        fresh = ["+" + k for k in keys[:32]]
        for name, get, put, delete in (("HashTable", table.get, table.put, table.delete),
                                        ("dict", ref.get, ref.__setitem__, ref.__delitem__)):
            read = bench(lambda: [get(k) for k in probes])
            update = bench(lambda: [put(k, 1) for k in probes])
            inserts = []
            for _ in range(REPEATS + 1):
                start = time.perf_counter()
                for key in fresh:
                    put(key, 1)
                inserts.append((time.perf_counter() - start) * 1e6 / len(fresh))
                for key in fresh:
                    delete(key)
            rows.append(("Операции", name, table.load_factor, read * 1e6 / N_PROBES,
                         update * 1e6 / N_PROBES, statistics.median(inserts[1:])))
    save_results(__file__, ("Серия", "Структура", "Загрузка α", "get, мкс", "put (обновление), мкс", "put (вставка), мкс"), rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check(seed)
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
