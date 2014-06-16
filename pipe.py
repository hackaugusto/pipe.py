'''
pipe is a simple utility to pass arguments around

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
'''
import unittest

try:
    from inject import inject
except ImportError:
    inject = None


def pipeit(klass, operator, plumber=None):
    '''
    This function creates a subclass of `value` that supports piping.
    Allowing the result to be used normally (except for the `operator`).
    '''

    def op(self, function):
        if plumber is not None:
            result = plumber(function, self)
        elif hasattr(self, 'keys') and hasattr(self, '__getitem__'):
            result = function(**self)
        elif hasattr(self, '__iter__'):
            result = function(*self)
        else:
            result = function(self)

        newklass = pipeit(result.__class__, operator, plumber=plumber)
        return newklass(result)

    return type('{}pipe'.format(klass.__name__), (klass,), {operator: op})


def pipe(value, operator='__or__', plumber=None):
    ''' tiny helper that creates the pipe class for value and instantiates it with value '''
    return pipeit(value.__class__, operator, plumber=plumber)(value)


if inject is not None:
    def plumberinject(function, data):
        result = inject(function, data)

        if hasattr(result, 'keys') and hasattr(result, '__getitem__'):
            # a mapping
            data.update(result)
        elif hasattr(result, '__iter__'):
            # assume a iterator with tuples of two values [(k, v), (k, v), ...]
            data.update(result)
        else:
            data[function.__name__] = result

        return data

    def pipeinject(value, operator='__or__', plumber=None):
        try:
            value = dict(value)
        except TypeError:
            raise TypeError('value must be a mapping')

        return pipeit(dict, operator, plumberinject)(value)

    class InjectTestCase(unittest.TestCase):
        def test_missing_argument(self):
            ''' missing arguments must raise a TypeError '''
            def function(a, b, *c):
                return 1

            with self.assertRaises(TypeError):
                pipeinject({}) | function

        def test_value(self):
            ''' A return value should be stored on the dictionary '''
            def function(a, b, *c):
                return 1

            arguments = {'a': 1, 'b': 2}
            result = pipeinject(arguments) | function
            arguments['function'] = 1
            self.assertEquals(arguments, result)

        def test_dict(self):
            ''' A return value that is a dictionary should be merged with data '''
            def function(a, b, *c):
                return {'d': 1}

            arguments = {'a': 1, 'b': 2}
            result = pipeinject(arguments) | function
            arguments['d'] = 1
            self.assertEquals(arguments, result)

        def test_override(self):
            ''' The return value from the dictionary has priority, it should override the data '''
            def function(a, b, *c):
                return {'a': 7}

            arguments = {'a': 1, 'b': 2}
            result = pipeinject(arguments) | function
            arguments['a'] = 7
            self.assertEquals(arguments, result)


if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', default=False, help='flag to run the tests')
    parser.add_argument('--failfast', action='store_true', default=False, help='unittest failfast')
    args = parser.parse_args()

    if args.test:
        import doctest
        (failures, total) = doctest.testmod()

        if failures:
            sys.exit(failures)

        if inject is not None:
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(InjectTestCase)
            result = unittest.TextTestRunner(failfast=args.failfast).run(suite)

            if result.errors or result.failures:
                sys.exit(len(result.errors) + len(result.failures))
