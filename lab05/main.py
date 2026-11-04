from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.lab_results import save_results

import argparse
import random
import statistics
import time
import traceback
from collections import deque


class Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    def __init__(self) -> None:
        self.root: Node | None = None

    def _traverse(self, order):
        keys = []

        def visit(node):
            if node is None:
                return
            if order == "pre":
                keys.append(node.key)
            visit(node.left)
            if order == "in":
                keys.append(node.key)
            visit(node.right)
            if order == "post":
                keys.append(node.key)

        visit(self.root)
        return keys

    def insert(self, key: int) -> None:
        if self.root is None:
            self.root = Node(key)
            return
        node = self.root
        while node.key != key:
            side = "left" if key < node.key else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, Node(key))
                return
            node = child

    def search(self, key: int) -> bool:
        node = self.root
        while node is not None:
            if node.key == key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        parent = None
        node = self.root
        while node is not None and key != node.key:
            parent, node = node, node.left if key < node.key else node.right
        if node is None:
            return
        if node.left is not None and node.right is not None:
            successor_parent, successor = node, node.right
            while successor.left is not None:
                successor_parent, successor = successor, successor.left
            node.key = successor.key
            parent, node = successor_parent, successor
        child = node.left if node.left is not None else node.right
        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child

    def in_order(self) -> list[int]:
        return self._traverse("in")

    def pre_order(self) -> list[int]:
        return self._traverse("pre")

    def post_order(self) -> list[int]:
        return self._traverse("post")

    def level_order(self) -> list[int]:
        keys = []
        queue = deque([self.root] if self.root else [])
        while queue:
            node = queue.popleft()
            keys.append(node.key)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return keys

    def height(self) -> int:
        height = -1
        level = [self.root] if self.root else []
        while level:
            height += 1
            level = [child for node in level for child in (node.left, node.right) if child]
        return height

    def size(self) -> int:
        return len(self.level_order())


class SelfCheckError(Exception):
    pass


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)


def build(keys) -> BST:
    tree = BST()
    for k in keys:
        tree.insert(k)
    return tree


def expect_search(tree: BST, key: int, present: bool, where: str) -> None:
    got = tree.search(key)
    expect(got is present, f"{where}: search({key}) вернул {got!r}, ожидалось {present}")


TRAVERSALS = ("in_order", "pre_order", "post_order", "level_order")


KNOWN_TREES = {
    (4, 2, 6, 1, 3, 5, 7): {
        "in_order": [1, 2, 3, 4, 5, 6, 7],
        "pre_order": [4, 2, 1, 3, 6, 5, 7],
        "post_order": [1, 3, 2, 5, 7, 6, 4],
        "level_order": [4, 2, 6, 1, 3, 5, 7],
        "height": 2,
        "size": 7,
    },
    (8, 3, 10, 1, 6, 14, 4, 7, 13): {
        "in_order": [1, 3, 4, 6, 7, 8, 10, 13, 14],
        "pre_order": [8, 3, 1, 6, 4, 7, 10, 14, 13],
        "post_order": [1, 4, 7, 6, 3, 13, 14, 10, 8],
        "level_order": [8, 3, 10, 1, 6, 14, 4, 7, 13],
        "height": 3,
        "size": 9,
    },
}


TWO_CHILDREN_CASES = [
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 3, [8, 4, 1, 6, 7, 10, 14, 13], [8, 1, 6, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 6, [8, 3, 1, 7, 4, 10, 14, 13], [8, 3, 1, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 8, [10, 3, 1, 6, 4, 7, 14, 13], [7, 3, 1, 6, 4, 10, 14, 13]),
    ((50, 30, 70, 60, 80, 65), 50, [60, 30, 70, 65, 80], [30, 70, 60, 65, 80]),
    ((50, 30, 70, 60, 80, 65), 70, [50, 30, 80, 60, 65], [50, 30, 65, 60, 80]),
]


def check_insert_search() -> None:
    tree = BST()
    expect_search(tree, 1, False, "пустое дерево")
    tree.insert(5)
    expect_search(tree, 5, True, "дерево из одного узла 5")
    expect_search(tree, 4, False, "дерево из одного узла 5")

    keys = [5, 2, 8, 1, 3, 9, 7]
    tree = build(keys)
    for k in range(11):
        expect_search(tree, k, k in keys, f"дерево из вставок {keys}")
    got = tree.in_order()
    expect(got == sorted(keys), f"in_order() после вставок {keys}: {got}, ожидалось {sorted(keys)}")
    tree.insert(5)
    tree.insert(1)
    got = tree.in_order()
    expect(got == sorted(keys), f"повторная вставка 5 и 1 изменила дерево: in_order() = {got}")


def check_traversals() -> None:
    empty = BST()
    for name in TRAVERSALS:
        got = getattr(empty, name)()
        expect(got == [], f"{name}() пустого дерева: {got}, ожидалось []")
    for keys, answer in KNOWN_TREES.items():
        tree = build(keys)
        for name in TRAVERSALS:
            got = getattr(tree, name)()
            expect(got == answer[name],
                   f"{name}() дерева из вставок {list(keys)}: {got}, ожидалось {answer[name]}")


def check_height_size() -> None:
    cases = [("пустое дерево", (), -1, 0), ("один узел 5", (5,), 0, 1)]
    cases += [(f"дерево из вставок {list(keys)}", keys, answer["height"], answer["size"])
              for keys, answer in KNOWN_TREES.items()]
    cases.append(("ключи 1, 2, …, 50 по возрастанию (цепочка)", tuple(range(1, 51)), 49, 50))
    for where, keys, height, size in cases:
        tree = build(keys)
        got_h, got_s = tree.height(), tree.size()
        expect(got_h == height, f"{where}: height() = {got_h}, ожидалось {height}")
        expect(got_s == size, f"{where}: size() = {got_s}, ожидалось {size}")


def check_delete() -> None:
    tree = BST()
    tree.delete(1)
    got = tree.in_order()
    expect(got == [], f"delete(1) из пустого дерева: in_order() = {got}")

    keys = [5, 2, 8, 1, 3]
    tree = build(keys)
    left = set(keys)
    steps = [(1, "лист 1"), (2, "узел 2 с одним ребёнком"), (5, "корень 5 с двумя детьми"),
             (4, "отсутствующий ключ 4"), (3, "ключ 3"), (8, "последний ключ 8")]
    for k, what in steps:
        tree.delete(k)
        left.discard(k)
        where = f"дерево из вставок {keys}, удаление: {what}"
        got = tree.in_order()
        expect(got == sorted(left), f"{where}: in_order() = {got}, ожидалось {sorted(left)}")
        expect_search(tree, k, False, where)
        for rest in left:
            expect_search(tree, rest, True, where)
    got_h, got_s = tree.height(), tree.size()
    expect(got_h == -1 and got_s == 0,
           f"после удаления всех ключей: height() = {got_h}, size() = {got_s}, ожидалось -1 и 0")


def check_delete_two_children() -> None:
    for keys, k, by_successor, by_predecessor in TWO_CHILDREN_CASES:
        tree = build(keys)
        tree.delete(k)
        where = f"delete({k}) в дереве из вставок {list(keys)}"
        rest = sorted(set(keys) - {k})
        got = tree.in_order()
        expect(got == rest, f"{where}: in_order() = {got}, ожидалось {rest}")
        got = tree.pre_order()
        expect(got in (by_successor, by_predecessor),
               f"{where}: pre_order() = {got}; при замене преемником ожидалось {by_successor}, "
               f"предшественником — {by_predecessor}")


def check_against_reference() -> None:
    rng = random.Random(0)
    for run in range(1, 101):
        tree = BST()
        etalon: set[int] = set()
        for step in range(1, rng.randint(1, 80) + 1):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                tree.insert(k)
                etalon.add(k)
                op = f"insert({k})"
            else:
                tree.delete(k)
                etalon.discard(k)
                op = f"delete({k})"

            got = tree.in_order()
            expect(got == sorted(etalon), f"прогон {run}, команда №{step} {op}: "
                                          f"in_order() = {got}, эталон {sorted(etalon)}")
        where = f"прогон {run}, итоговое дерево"
        for k in range(-30, 31):
            expect_search(tree, k, k in etalon, where)
        n = len(etalon)
        got = tree.size()
        expect(got == n, f"{where}: size() = {got}, эталон {n}")
        for name in TRAVERSALS[1:]:
            got = getattr(tree, name)()
            expect(sorted(got) == sorted(etalon), f"{where}: {name}() содержит не те ключи: {got}")
        got = tree.height()
        low, high = (-1, -1) if n == 0 else (n.bit_length() - 1, n - 1)
        expect(low <= got <= high,
               f"{where}: height() = {got} при {n} узлах, возможно от {low} до {high}")


def self_check() -> None:
    checks = (
        ("вставка и поиск", check_insert_search),
        ("обходы", check_traversals),
        ("высота и размер", check_height_size),
        ("удаление", check_delete),
        ("удаление узла с двумя детьми", check_delete_two_children),
        ("сверка с эталоном set/sorted", check_against_reference),
    )
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
QUERIES = 1_000


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
    rows = []
    for n in SIZES:
        keys = rng.sample(range(10 * n), n)
        queries = [rng.randrange(10 * n) for _ in range(QUERIES)]
        tree = build(keys)
        for name, search in (("BST", tree.search), ("list", keys.__contains__)):
            duration = bench(lambda: [search(k) for k in queries])
            rows.append(("Поиск", name, n, duration / QUERIES * 1e6, tree.height()))
    save_results(__file__, ("Серия", "Структура", "n", "Время, мкс", "Высота BST"), rows, metrics=(3,))


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
