"""Methods and classes to handle Cement Hook support."""

from cement.core.backend import hooks, minimal_logger
from cement.core.exc import CementRuntimeError

log = minimal_logger(__name__)

def define(name):
    """
    Define a hook namespace that plugins can register hooks in.
    
    Required arguments:
    
        name
            The name of the hook, stored as hooks['name']
    
    
    Usage:
    
    .. code-block:: python
    
        from cement.core import hook
        
        hook.define('myhookname_hook')
    
    """
    log.debug("defining hook '%s'", name)
    if hooks.has_key(name):
        raise CementRuntimeError, "Hook name '%s' already defined!" % name
    hooks[name] = []
    
    
class register(object):
    """
    Decorator function for plugins to register hooks.  Used as:
    
    Optional keyword arguments:
    
        weight
            The weight in which to order the hook function (default: 0)
        
        name
            The name of the hook to register too.  If not passed, the __name__
            of the decorated function will be used.

    Usage:
    
    .. code-block:: python
        
        from cement.core import hook
        
        @hook.register()
        def my_hook(*args, **kwargs):
            # do something here
            res = 'Something to return'
            return res
    
    """
    def __init__(self, weight=0, name=None):
        self.weight = weight
        self.name = name

    def __call__(self, func):
        if not self.name:
            self.name = func.__name__
        log.debug("registering hook func '%s' from %s into hooks['%s']" % \
            (func.__name__, func.__module__, self.name))
        if not hooks.has_key(self.name):
            log.debug("hook name '%s' is not defined!" % self.name)
            return func

        # Hooks are as follows: (weight, name, func)
        hooks[self.name].append((int(self.weight), func.__name__, func))


def run(name, *args, **kwargs):
    """
    Run all defined hooks in the namespace.  Yields the result of each hook
    function run.
    
    Optional arguments:
    
        name
            The name of the hook function
        args
            Any additional args are passed to the hook function
        kwargs
            Any kwargs are passed to the hook function
    
    
    Usage:
    
    .. code-block:: python
    
        from cement.core import hook
        
        for result in hook.run('hook_name'):
            # do something with result from each hook function
            ...
    """
    if not hooks.has_key(name):
        raise CementRuntimeError, "Hook name '%s' is not defined!" % name
    hooks[name].sort() # Will order based on weight
    for hook in hooks[name]:
        log.debug("running hook '%s' (%s) from %s" % (name, hook[2], hook[2].__module__))
        res = hook[2](*args, **kwargs)
        
        # Results are yielded, so you must fun a for loop on it, you can not
        # simply call run_hooks().  
        yield res