#!/usr/bin/env python
import operator
import math
from collections.abc import KeysView, ValuesView, ItemsView
from functools import partial
from unittest.mock import patch

import pytest

from coordinates.classes import MathDict, Coordinate, spaced_coordinate


def literal(n):
    return n


ntypes = (literal, abs, int, float)

unary_ops = (
    operator.neg, operator.pos, operator.abs,
    math.ceil, math.floor, math.trunc, partial(round, ndigits=1)
)

binary_ops = (
    operator.add, operator.sub, operator.mul, operator.floordiv, operator.truediv, operator.mod, operator.pow,
    operator.iadd, operator.isub, operator.imul, operator.ifloordiv, operator.itruediv, operator.imod, operator.ipow
)


@pytest.fixture(params=[5.5, {'a': 5, 'b': 15, 'c': -30.5}], ids=['number', 'dict'])
def operand(request):
    return request.param


@pytest.fixture
def keys_vals():
    return ('a', 10), ('b', -20), ('c', 1.5)


class TestMathDict(object):
    Class = MathDict

    @pytest.mark.parametrize('args,kwargs', [
        ([{'a': 1, 'b': 2, 'c': 3}], dict()),
        ([], {'a': 1, 'b': 2, 'c': 3}),
        ([{'a': 1, 'b': 2}], {'c': 3}),
        ([[('a', 1), ('b', 2), ('c', 3)]], dict()),
    ])
    def test_instantiate_like_dict(self, args, kwargs):
        self.Class(*args, **kwargs)

    @pytest.mark.parametrize('ntype', ntypes)
    @pytest.mark.parametrize('op', unary_ops)
    def test_unary_ops(self, op, ntype, keys_vals):
        result = op(self.Class([(key, ntype(val)) for key, val in keys_vals]))
        for key, val in keys_vals:
            assert result[key] == op(ntype(val))

    @pytest.mark.parametrize('ntype', ntypes)
    @pytest.mark.parametrize('op', binary_ops)
    def test_binary_ops(self, op, ntype, operand, keys_vals):
        result = op(self.Class([(key, ntype(val)) for key, val in keys_vals]), operand)
        for key, val in keys_vals:
            try:
                other = operand[key]
            except TypeError:
                other = operand
            assert result[key] == op(ntype(val), other)

    def test_sum(self, keys_vals):
        obj = self.Class(keys_vals)
        expected = 0
        for _, val in keys_vals:
            expected += val

        assert obj.sum() == expected

    def test_prod(self, keys_vals):
        obj = self.Class(keys_vals)
        expected = 1
        for _, val in keys_vals:
            expected *= val

        assert obj.prod() == expected

    @pytest.mark.parametrize('order', [1, 2])
    def test_norm(self, keys_vals, order):
        obj = self.Class(keys_vals)
        expected = (sum(abs(val) ** order for _, val in keys_vals)) ** (1 / order)
        assert obj.norm(order) == pytest.approx(expected)

    def test_getattr(self):
        obj = self.Class(a=1, b=2, c=3)
        assert obj.a == 1
        assert obj.b == 2
        assert obj.c == 3


class TestCoordinate(TestMathDict):
    Class = Coordinate

    @pytest.mark.parametrize('args', [(1, 2, 3), ([1, 2, 3],)])
    def test_instantiate_from_order(self, args):
        obj = self.Class(*args, order='abc')
        assert obj == {'a': 1, 'b': 2, 'c': 3}

    @pytest.mark.parametrize('args', [(1, 2, 3), ([1, 2, 3],)])
    def test_instantiate_from_default_order(self, args):
        try:
            old_order = self.Class.default_order
            self.Class.default_order = 'abc'
            obj = self.Class(*args)
            assert obj == {'a': 1, 'b': 2, 'c': 3}
        finally:
            self.Class.default_order = old_order

    @pytest.mark.parametrize('order,expected_order', [('cba', 'cba'), ('abc', 'abc')])
    def test_order(self, keys_vals, order, expected_order):
        obj = self.Class(keys_vals, order=order)
        assert obj.order == expected_order

    @pytest.mark.parametrize('order', [None, 'cba', 'abc'])
    def test_to_list(self, keys_vals, order):
        obj = self.Class(keys_vals)
        if order is None:
            order = obj.order

        d = dict(keys_vals)
        expected_list = [d[key] for key in order]

        assert obj.to_list(order) == expected_list

    @pytest.mark.parametrize('order', [None, 'cba', 'abc'])
    @pytest.mark.parametrize('method,view_type', [
        ('keys', KeysView),
        ('values', ValuesView),
        ('items', ItemsView),
    ])
    def test_views_types(self, keys_vals, order, method, view_type):
        obj = self.Class(keys_vals)
        if order is None:
            order = obj.order

        view = getattr(obj, method)(order)
        assert isinstance(view, view_type)

        d = dict(keys_vals)

        if method == 'keys':
            assert list(view) == list(order)
        if method == 'values':
            assert list(view) == [d[key] for key in order]
        if method == 'items':
            assert list(view) == [(key, d[key]) for key in order]


class TestSpacedCoordinate(TestCoordinate):
    Class = spaced_coordinate('CoordinateCAB', 'cab')

    def test_order_is_set(self):
        obj = self.Class(a=1, b=2, c=3)
        assert obj.order == 'cab'

    def test_bad_keys_raises(self):
        with pytest.raises(ValueError, match='needs keys'):
            self.Class(d=5)


if __name__ == '__main__':
    pytest.main(['test_classes.py::TestCoordinate::test_instantiate_from_order'])
