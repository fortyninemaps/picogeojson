
def docstring_insert(*s):
    def wrapped(obj):
        try:
            obj.__doc__ = obj.__doc__.format(*s)
        except (AttributeError, TypeError):
            # class __doc__ attribute not writable in Python 2
            # and in PyPy an TypeError is raised rather than an AttributeError
            pass
        return obj
    return wrapped

