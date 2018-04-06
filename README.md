# coordinates

[![Build Status](https://travis-ci.org/clbarnes/coordinates.svg?branch=master)](https://travis-ci.org/clbarnes/coordinates)

Convenience class for dealing with coordinates which need both maths and explicit ordering.

Supports python 3.4+

## Motivation

Numpy arrays are great for doing maths with coordinates stored as arrays.

Dicts are great for dealing with coordinate systems where the order keeps changing 
(e.g. between C and Fortran order).

But what if you want both?

(Note: if you're doing *lots* of maths... stick with `numpy`)

## Installation

```bash
pip install coordinates
```

## Usage

`Coordinate`s are `Mapping`s (i.e. `dict`-like). They don't expose an interface for mutation, but
we're all consenting adults so if you really want to modify the internal `_dict`, I won't
stop you.

### Instantiation

They can be instantiated in any of the ways a `dict` can (from another `Mapping`, a sequence of pairs,
some keyword arguments, or a mixture of the above).

```python
from coordinates import Coordinate

Coordinate({'x': 1, 'y': 2})
Coordinate({'x': 1}, y=2)
Coordinate([('x', 1), ('y', 2)])
Coordinate(x=1, y=2)
```

If an order is defined (more on this later), you can also instantiate a `Coordinate` from a single 
argument which is a sequence, or from a number of `*args`.

```python
Coordinate([1, 2], order='xy')
Coordinate(1, 2, order='xy')

Coordinate.default_order = 'xy'
Coordinate([1, 2])
Coordinate(1, 2)
```

Because `Mapping`s can be instantiated from other `Mapping`s, you can "extend" existing coordinates 
into new dimensions.

```python
coord_2d = Coordinate(x=1, y=2)
coord_3d = Coordinate(coord_2d, z=3)
```

Finally, many `Coordinate`s can be instantiated lazily using `from_sequence`:

```python
Coordinate.from_sequence([(1, 2, 3), (3, 4, 5)], order='xyz')
Coordinate.from_sequence([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}], z=10)
```

To note: 

- `order`-dependent instantiation is incompatible with `**kwargs`
- Instantiation from a sequence of tuples will fail in 2D because it will be interpreted as 
key-value pairs. Use a comprehension here instead: `Coordinate.from_sequence(zip('xy', row) for row in sequence)`

### Maths

Coordinates do maths like you might expect them to, where the other operand is anything dict-like
with the same keys, or a number.

```python
coord = Coordinate(x=1, y=2, z=3)

coord * 2 == Coordinate(x=2, y=4, z=6)
>>> True

coord ** 2 == Coordinate(x=1, y=4, z=9)
>>> True

coord + coord == Coordinate(x=2, y=4, z=3)
>>> True

coord += 1  # coord is a reference to a new object; no mutation
coord == Coordinate(x=2, y=3, z=4)
>>> True

abs(Coordinate(x=-10, y=10)) == Coordinate(x=10, y=10)
>>> True

import math
math.ceil(Coordinate(x=0.5)) == Coordinate(x=1)
>>> True

math.floor(Coordinate(x=0.5)) == Coordinate(x=0)
>>> True
```

They also have some convenience methods for getting the sum, product or norm of their keys.

```python
coord.sum() == 9
>>> True

coord.prod() == 24
>>> True

Coordinate(x=3, y=4).norm(order=2) == 5
>>> True
```

### Ordering

You can get the keys, values or items of the `Coordinate` in a specific order:

```python
coord.to_list('yxz') == [2, 1, 3]
>>> True

list(coord.items('yxz')) == [('y', 2), ('x', 1), ('z', 3)]
>>> True
```

The default order for a single instance can be given on instantiation, or mutated (this does not affect equality).

The default order for all `Coordinate`s can be set on the class. This affects existing instances, but does not 
override their order if it was set explicitly.

If neither an instance `order` or a class `default_order` is set, it falls back to reverse lexicographic.

```python
coord3 = Coordinate(x=1, y=2, z=3, order='zxy')
coord3.order = 'yzx'

Coordinate.default_order = 'xyz'
```

### Subclassing

If you're working in one space, the `spaced_coordinate` factory can create custom subclasses with a fixed set of
keys and optionally a default order.

```python
from coordinates import spaced_coordinate
CoordinateXYZC = spaced_coordinate('CoordinateXYZC', 'xyzc')

# this will raise a ValueError
CoordinateXYZC(x=1, y=2, z=3)
```

Or you can subclass `Coordinate` directly.

### Value access

Coordinate values can be accessed with dict-like syntax (`coord['x']`, `coord.get('y', 2)`) or, for convenience,
attribute-like (`coord.z`) if the keys are strings.

## Note

If you don't want the order-related functionality for another application, the base class `MathDict` is 
implemented here too.
