pipe.py
-------

pipe is a simple utility to pass arguments around

```python
>>> pipe(5) | (lambda x: x**2) | (lambda x: x-3)
22

>>> pipe((5, 3)) | (lambda x, y: (x**2, y/2) ) | (lambda x, y: x) | (lambda x: x-3)
22

>>> def add(**values):
...     return {k: sum(v) for k, v in values.items()}
>>> def even(**values):
...     return {k: v for k, v in values.items() if v % 2 == 0}
>>> pipe({'a': [1, 2, 3], 'b': [7, 0, 11], 'c': [3, 4]}) | add | even | (lambda **values: sorted(values.keys()))
['a', 'b']
```
