import operator
from collections import OrderedDict
from numbers import Number
from collections.abc import Mapping, KeysView, ValuesView, ItemsView

import math

__all__ = ['Coordinate', 'spaced_coordinate']


class MathDict(Mapping):
    """
    Class with a dict-like API which can have maths done to it, where the other operand is either another MathDict with
    the same keys or a number.
    """

    def __init__(self, *args, **kwargs):
        """
        Instantiate like a dict.
        """
        self._dict = dict(*args, **kwargs)

    def __getitem__(self, item):
        return self._dict[item]

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(self).__name__, item))

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '{class_name}({d})'.format(class_name=type(self).__name__, d=self._dict)

    def __round__(self, n=None):
        return type(self)({key: round(val, n) for key, val in self.items()})

    def __unary_op(self, op):
        return type(self)({key: op(val) for key, val in self.items()})

    def __neg__(self):
        return self.__unary_op(operator.neg)

    def __pos__(self):
        return self.__unary_op(operator.pos)

    def __abs__(self):
        return self.__unary_op(operator.abs)

    def __ceil__(self):
        return self.__unary_op(math.ceil)

    def __floor__(self):
        return self.__unary_op(math.floor)

    def __trunc__(self):
        return self.__unary_op(math.trunc)

    def __binary_op(self, op, other):
        if isinstance(other, Number):
            other = {key: other for key in self.keys()}
        elif not self.keys() == other.keys():
            raise KeyError('{} and {} do not have the same keys'.format(self, other))
        return type(self)({key: op(val, other[key]) for key, val in self.items()})

    def __add__(self, other):
        return self.__binary_op(operator.add, other)

    def __sub__(self, other):
        return self.__binary_op(operator.sub, other)

    def __mul__(self, other):
        return self.__binary_op(operator.mul, other)

    def __floordiv__(self, other):
        return self.__binary_op(operator.floordiv, other)

    def __truediv__(self, other):
        return self.__binary_op(operator.truediv, other)

    def __mod__(self, other):
        return self.__binary_op(operator.mod, other)

    def __pow__(self, other):
        return self.__binary_op(operator.pow, other)

    def __iadd__(self, other):
        return self.__binary_op(operator.iadd, other)

    def __isub__(self, other):
        return self.__binary_op(operator.isub, other)

    def __imul__(self, other):
        return self.__binary_op(operator.imul, other)

    def __ifloordiv__(self, other):
        return self.__binary_op(operator.ifloordiv, other)

    def __itruediv__(self, other):
        return self.__binary_op(operator.itruediv, other)

    def __imod__(self, other):
        return self.__binary_op(operator.imod, other)

    def __ipow__(self, other):
        return self.__binary_op(operator.ipow, other)

    def sum(self):
        return sum(self.values())

    def prod(self):
        p = 1
        for val in self.values():
            p *= val
        return p

    def norm(self, order=2):
        return (sum(val**order for val in abs(self).values()))**(1/order)


class Coordinate(MathDict):
    """
    Class with coordinate in arbitrary space in whatever order is requested. Change the class' default ordering with
    ``Coordinate.default_order = 'xyz'``

    Coordinates can have maths done to do them, with either another Coordinate instance with the same keys (order
    independent) or a number.
    """
    default_order = None

    def __init__(self, *args, order=None, **kwargs):
        """
        Instantiate like a dict, with the exception of kwarg ``order``, which specifies the instance's default dimension
        ordering.

        If the class has no ``default_order`` and no ``order`` kwarg is given, order will be set as reverse
        lexicographic.
        """
        super().__init__(*args, **kwargs)
        self._order = order
        self._validate()

    @property
    def order(self):
        return self._order or self.default_order or sorted(self._dict, reverse=True)

    @order.setter
    def order(self, value):
        self._order = value

    def __setitem__(self, key, value):
        raise NotImplementedError('Items cannot be set')

    def to_list(self, order=None):
        return list(self.values(order))

    def __iter__(self):
        return iter(self.keys())

    def _to_ordered_dict(self, order):
        return OrderedDict((key, self[key]) for key in order if key in self)

    def keys(self, order=None):
        return KeysView(self._to_ordered_dict(order or self.order))

    def values(self, order=None):
        return ValuesView(self._to_ordered_dict(order or self.order))

    def items(self, order=None):
        return ItemsView(self._to_ordered_dict(order or self.order))

    def __repr__(self):
        keyvals = ', '.join("{}: {}".format(repr(key), value) for key, value in self.items())
        return '{class_name}({{{keyvals}}})'.format(class_name=type(self).__name__, keyvals=keyvals)

    def _validate(self):
        pass  # to be overridden in subclasses


def spaced_coordinate(name, keys, ordered=True):
    def validate(self):
        if set(keys) != set(self):
            raise ValueError('{} needs keys {} and got {}'.format(type(self).__name__, keys, tuple(self)))

    new_class = type(name, (Coordinate, ), {'default_order': keys, '_validate': validate})
    return new_class
