"""
data_structures.py
Hand-written data structures used by all programs (no collections / heapq /
sorted() / library graph routines are used anywhere in this assignment).

    Queue      - FIFO queue (array + head index)        -> BFS
    Stack      - LIFO stack                             -> iterative DFS
    MinHeap    - binary min-heap (priority queue)       -> Prim
    merge_sort - stable merge sort on a key function    -> Kruskal
    DSU        - disjoint set union (path compression + union by rank) -> Kruskal
"""


class Queue:
    """FIFO queue. enqueue/dequeue are O(1) (head index instead of pop(0))."""

    def __init__(self):
        self._items = []
        self._head = 0

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        item = self._items[self._head]
        self._head += 1
        return item

    def is_empty(self):
        return self._head >= len(self._items)

    def size(self):
        return len(self._items) - self._head


class Stack:
    """LIFO stack. push/pop are O(1)."""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        return self._items.pop()

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)


class MinHeap:
    """Binary min-heap of (key, payload) pairs. push/pop_min are O(log n)."""

    def __init__(self):
        self._a = []

    def is_empty(self):
        return len(self._a) == 0

    def size(self):
        return len(self._a)

    def push(self, key, payload):
        a = self._a
        a.append((key, payload))
        i = len(a) - 1
        while i > 0:
            p = (i - 1) // 2
            if a[p][0] > a[i][0]:
                a[p], a[i] = a[i], a[p]
                i = p
            else:
                break

    def pop_min(self):
        a = self._a
        top = a[0]
        last = a.pop()
        if len(a) > 0:
            a[0] = last
            i, n = 0, len(a)
            while True:
                l, r, s = 2 * i + 1, 2 * i + 2, i
                if l < n and a[l][0] < a[s][0]:
                    s = l
                if r < n and a[r][0] < a[s][0]:
                    s = r
                if s == i:
                    break
                a[s], a[i] = a[i], a[s]
                i = s
        return top


def merge_sort(items, key):
    """Stable merge sort (ascending by key(item)). O(n log n) time, O(n) space."""
    n = len(items)
    if n <= 1:
        return list(items)
    mid = n // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):      # strict '<' keeps the sort stable
            out.append(right[j]); j += 1
        else:
            out.append(left[i]); i += 1
    while i < len(left):
        out.append(left[i]); i += 1
    while j < len(right):
        out.append(right[j]); j += 1
    return out


class DSU:
    """Disjoint-set union with path compression and union by rank: O(alpha(n)) per op."""

    def __init__(self, n):
        self.parent = [i for i in range(n)]
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True