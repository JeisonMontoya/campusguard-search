"""Provides some utilities widely used by other modules - Simplified version without numpy"""

from __future__ import annotations

import bisect
import collections
import collections.abc
import functools
import heapq
import operator
import os.path
import random
from itertools import chain, combinations
from statistics import mean


# ______________________________________________________________________________
# Functions on Sequences and Iterables


def sequence(iterable):
    """Converts iterable to sequence, if it is not already one."""
    return iterable if isinstance(iterable, collections.abc.Sequence) else tuple([iterable])


def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]


def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements."""
    return list(set(seq))


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))


def multimap(items):
    """Given (key, val) pairs, return {key: [val, ...], ...}."""
    result = {}
    for key, val in items:
        result.setdefault(key, []).append(val)
    return result


def is_in(elt, seq):
    """Return True if elt is in seq."""
    return elt in seq


def identity(x):
    """Identity function."""
    return x


def argmax_random_tie(seq, key=identity):
    """Return an element with highest key(seq) score; break ties randomly."""
    return max(seq, key=lambda x: (key(x), random.random()))


def argmin_random_tie(seq, key=identity):
    """Return an element with lowest key(seq) score; break ties randomly."""
    return min(seq, key=lambda x: (key(x), random.random()))


def shuffled(iterable):
    """Randomly shuffle a copy of iterable."""
    items = list(iterable)
    random.shuffle(items)
    return items


# ______________________________________________________________________________
# Functions on Numbers and Math


def inverse(x):
    """Inverse function."""
    return 1 / x if x != 0 else float('inf')


def normalize(probs):
    """Normalize a list of numbers to sum to 1."""
    total = sum(probs)
    if total == 0:
        return [0] * len(probs)
    return [p / total for p in probs]


def clip(x, min_val, max_val):
    """Clip x to be within [min_val, max_val]."""
    return max(min_val, min(x, max_val))


# ______________________________________________________________________________
# Data Structures


class PriorityQueue:
    """A queue in which the item with minimum f(item) is popped first."""
    
    def __init__(self, order=min, f=lambda x: x):
        self.heap = []
        self.f = f
        self.order = order  # min or max
    
    def append(self, item):
        """Add item to the queue."""
        heapq.heappush(self.heap, (self.f(item), item))
    
    def pop(self):
        """Remove and return the item with minimum f value."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise IndexError("pop from empty priority queue")
    
    def __len__(self):
        return len(self.heap)
    
    def __contains__(self, item):
        return any(item == pair[1] for pair in self.heap)
    
    def __getitem__(self, key):
        for _, item in self.heap:
            if item == key:
                return item
        raise KeyError(key)
    
    def __delitem__(self, key):
        for i, (_, item) in enumerate(self.heap):
            if item == key:
                del self.heap[i]
                heapq.heapify(self.heap)
                return
        raise KeyError(key)


# ______________________________________________________________________________
# Statistical Functions (replacing numpy functions)


def mean(values):
    """Return the mean of a list of values."""
    return sum(values) / len(values) if values else 0


def stdev(values):
    """Return the standard deviation of a list of values."""
    if len(values) < 2:
        return 0
    m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


# ______________________________________________________________________________
# Vector/Matrix Operations (minimal replacements for numpy)


def dot(v1, v2):
    """Dot product of two vectors."""
    return sum(a * b for a, b in zip(v1, v2))


def add(v1, v2):
    """Element-wise addition of two vectors."""
    return [a + b for a, b in zip(v1, v2)]


def subtract(v1, v2):
    """Element-wise subtraction of two vectors."""
    return [a - b for a, b in zip(v1, v2)]


def scalar_multiply(scalar, vector):
    """Scalar multiplication of a vector."""
    return [scalar * x for x in vector]


def vector_norm(vector):
    """Euclidean norm of a vector."""
    return sum(x * x for x in vector) ** 0.5


def normalize_vector(vector):
    """Normalize a vector to unit length."""
    norm = vector_norm(vector)
    if norm == 0:
        return vector
    return [x / norm for x in vector]


# ______________________________________________________________________________
# Other Utilities


def memoize(fn, slot=None):
    """Memoize fn: make it remember the computed value for any argument list."""
    if slot:
        def memoized_fn(obj, *args):
            if not hasattr(obj, slot):
                setattr(obj, slot, {})
            memo = getattr(obj, slot)
            if args not in memo:
                memo[args] = fn(obj, *args)
            return memo[args]
    else:
        memo = {}
        def memoized_fn(*args):
            if args not in memo:
                memo[args] = fn(*args)
            return memo[args]
    return memoized_fn


def name(obj):
    """Return the name of an object."""
    return getattr(obj, '__name__', str(obj))


# Export commonly used names
__all__ = [
    'sequence', 'remove_all', 'unique', 'count', 'multimap', 'is_in',
    'argmax_random_tie', 'argmin_random_tie', 'shuffled',
    'identity', 'inverse', 'normalize', 'clip',
    'PriorityQueue',
    'mean', 'stdev',
    'dot', 'add', 'subtract', 'scalar_multiply', 'vector_norm', 'normalize_vector',
    'memoize', 'name',
]