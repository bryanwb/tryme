======================================================================
tryme - Error handling for humans
======================================================================


Introduction
============


What?
-----

Tryme is a module that makes it easier to treat errors as values. Additionally,
tryme helps you handle the absence of a value (None) in a more composable way.

The entire tryme library is contained in a single file `tryme.py` to
make it as easy as possible to drop into an existing project.

Why?
----

Treating errors as values makes it easier to retain information related to errors and
lets us defer error handling until the last possible moment. In contrast, exceptions are
fundamentally lossy in they by convention contain tracebacks and error messages not values.
Additionally, they require immediate handling.

Here are a few tasks where we might wish to defer error handling.

* Processing multiple operations in batch where one or more operations may fail
* Executing long running operations that require multiple retries

Treating failed operations as values rather than exceptions can simplify conditional logic and
make programs more composable.
  
*But c'mon that is unpythonic*

A common convention for handling errors in Python is to raise exceptions. There
is no reason however that this is always the best mechanism to handle errors,
especially *expected errors*. The author of this package feels strongly
that exceptions are best used to represent exceptional circumstances
such as when undefined behavior is encountered.


Treating Errors as Values
------------------------------

Python does not have a built-in convention for treating errors as values
other than try/except.

tryme introduces the Failure/Success convention of wrapping failed or
successful results in a container class.

Here is how an error might be treated using good old ``try/except``::

  import requests


  def google_is_accessible():
      response = requests.get('http://google.com')
      if response.ok:
          return response.ok
      else:
          raise RuntimeError("http request to google.com failed with status code %s" % response.status_code)

   try:
       is_accessible = google_is_accessible()
   except RuntimeError:
       is_accessible = False


Here is the same task using the ``tryme.Success`` and ``tryme.Failure``::

  import requests


  def google_is_accessible():
      response = requests.get('http://google.com')
      if response.ok:
          return Success(response)
      else:
          return Failure(response)

   result = google_is_accessible()
   is_accessible = result.succeeded()
   # In the result value, we still have access to all of the information about the response


The utility method ``try_out`` executes a callable and wraps a raised exception
in a Failure class. If an exception was not raised, a Success is returned

::

  >>> from tryme import try_out
  >>> result = try_out(lambda: 1 / 0)
  >>> print result
  Failure(ZeroDivisionError('integer division or modulo by zero',))
  >>> exc = result.value
  >>> exc
  ZeroDivisionError('integer division or modulo by zero',)
  >>> # the following would fail as it does not catch the correct exception, ZeroDivisionError
  >>> # result = try_out(lambda: 1 / 0, exception=ValueError)
  >>> result = try_out(lambda: 1 / 1)
  >>> print result
  Success(1)
  >>> result.value
  1

      
Retrying with Style
---------------------------------------------------

Let's say we want to create a single server using a new Cloud computing provider named
HighlyVariable Inc. HighlyVariable can provision our new server in a few seconds, several minutes,
or occasionally not at all. This author has used cloud services where the "not at all" is not so
uncommon an outcome!

Let's create a `server_ready` function that returns a `Success` when the server
is ready, a `Failure` when the operation times out. A "terminal" state such as
"Ready" or "Failed" will terminate retries immediately whereas a Failed will
continue execution of the `server_ready` function until 300 seconds after the
function was first called.

If our new server is not ready after 300 seconds, `server_ready` will return an
instance of `Failure`.

::

   from highlyvariable import create_instance, get_instance_status
   from tryme import retry_decorator

   def make_server(name):
       create_instance(name)
       
   
   @retry
   def wait_for_server_statuses(name, statuses):
       status = get_instance_status(name)
       if status in statuses:
           return Success(status)
       else:
           return Failure("Not ready yet")

           
   def server_ready(name):
       # the decorated function will return two values, a log accounting for the time spent retrying
       # and the actual result
       log, result = wait_for_server_statuses(name, ['Ready', 'Failed'])
       # a failure here only indicates a timeout
       if result.failed():
           return Failure("Server %s not ready after %d seconds" % (name, log.elapsed))

       # unwrap the value
       status = result.get()
       if status == 'Ready':
           return Success('server %s is ready after %d seconds and %d attempts!"
                          % (name, log.elapsed, log.count))
       else:
           return Failure('server %s failed after %d seconds!"
                          % (name, log.elapsed))

   make_server('jenkins')
   result = server_ready('jenkins')
   assert result.succeeded()
   # prints "Server jenkins is ready after n seconds and n attempts!"
   result.to_console()
   

 
There something a little weird about the above example. Why did we return Success when the status was
"Failed"? This is because the return value of Failure in the wrapped function is a signal to the `@retry` decorator to continue retrying until the timeout is reached or an exception is raised. 




Requirements
============

- CPython >= 2.7


Background
============

This package is inspired by Philip Xu's excellent `monad package <https://github.com/pyx/monad>`_.
It also takes some inspiration from the excellent `vavr <https://vavr.io>`_ library for java and the Scala language.
See this excellent `tutorial <http://danielwestheide.com/blog/2012/12/26/the-neophytes-guide-to-scala-part-6-error-handling-with-try.html>`_
on the Try utility in Scala.

Pssssh! While this package uses *gasp* monads as the core abstraction it does not provide
general purpose implementations of monad, applicatives, and functors. Further it does
not attempt to overload common Python operators to support function composition.


Installation
============

Install from PyPI::

  pip install smonad

Install from source, download source package, decompress, then ``cd`` into source directory, run::

  make install


License
=======

BSD New, see LICENSE for details.


Links
=====

Documentation:
  http://smonad.readthedocs.org/

Issue Tracker:
  https://github.com/bryanwb/smonad/issues/

Source Package @ PyPI:
  https://pypi.python.org/pypi/smonad/

Git Repository @ Github:
  https://github.com/bryanwb/smonad/
