======================================================================
tryme - Error handling for humans
======================================================================


Introduction
============

Tryme is a module that makes it easier to treat errors as values. Additionally,
tryme helps you handle the absence of a value (None) in a more composable way.

The entire tryme library is contained in a single file `tryme.py` to
make it as easy as possible to drop into an existing project or script.

Why should I care?
--------------------
  
Treating errors as values makes it easier to retain information related to errors and
lets us defer error handling until the last possible moment. In contrast, exceptions are
fundamentally lossy in they by convention contain tracebacks and error messages not values.
Further, exceptions abort execution by default and break normal code flow.

Here are a few tasks where we might wish to defer error handling.

* Processing multiple operations in batch where one or more operations may fail
* Executing long running operations that require multiple retries

Treating failed operations as values rather than exceptions can simplify conditional logic and
make programs more composable.
  
*But c'mon exceptions are pythonic*

A common convention for handling errors in Python is to raise exceptions. There
is no reason however that this is always the best mechanism to handle errors,
especially *expected errors*. The author of this package feels strongly
that exceptions are best used to represent exceptional circumstances
such as when undefined behavior is encountered.


Error Handling Strategies
------------------------------

A good error handling strategy retains relevant information and defers side
effects related to a failure as long as possible to allow upstream code to
decide how to handle the failure.

Here are four error handling strategies that I have encountered:

1. Return a boolean to indicate success/failure
2. Return a tuple of (err, value) where err represents a possible error and value
   is well, a value
3. Return a value for success and raise an exception in the case of an error
4. Return a value in case of success and a custom Error class that contains information
   about the failure but is not necessarily a subclass of `Exception`
5. Return an instance of Success or Failure containing a value


Strategy #1 Return a boolean
-------------------------------

The simplest possible strategy is to return a boolean to indicate the success or
failure. For a simple example, let's build a trivial program to check if Google is accessible.

Our first iteration will simply return a boolean to indicate if Google is accessible.
::

  import requests


  def google_is_accessible():
      response = requests.get('http://google.com')
      return response.ok

  is_accessible = google_is_accessible()
  if is_accessible:
      print('It works!')
  else:
      print('Google is not accessible. No idea why')

Awesome! We now can check if Google is accessible from our remote location. The big drawback
is that `google_is_accessible` doesn't tell me what went wrong in case of a failure nor
does give any information to figure that out for myself.


Strategy #2 Return a tuple of (err, value)
---------------------------------------------

A similar approach is to return a tuple of (err, value) where err indicates if an error
occurred. This approach is idiomatic in the Go programming language.
::

  import requests


  def google_is_accessible():
      response = requests.get('http://google.com')
      return response.ok, response

  is_accessible, response = google_is_accessible()
  if is_accessible:
      print('It works!')
  else:
      print('Google is not accessible, received http status %s' % response.status_code)


This is a big improvement! We now can determine what went wrong should we care.

The main drawback of returning a tuple to indicate errors is that it makes it harder to
compose functions. Let's extend our simple example to try multiple search engines in case
Google is not accessible.::

  import requests


  def duck_duck_go_is_accessible():
      response = requests.get('http://google.com')
      return response.ok, response

  
  def google_is_accessible():
      response = requests.get('http://google.com')
      return response.ok, response

      
  is_accessible, response = google_is_accessible()
  if is_accessible:
      print('It works! Using Google')
  else:
      print('Google is not accessible, received http status %s. Trying duckduckgo'
            % response.status_code))
      is_accessible, response = duck_duck_go_is_accessible()
      if is_accessible:
           print('It works! Using DuckDuckGo')
      else:
           print('DuckDuckGo is not accessible, received http status %s. Out of options'
                 % response.status_code))

The conditionals in the above example can be reduced but it is apparent that returning a tuple
adds more conditional logic to your code.

Strategy #3 Raise an Exception
---------------------------------

Here is our example using good old ``try/except``::

  import requests


  class GoogleNotAccessibleError(Exception):
      pass
  
  
  def google_is_accessible():
      response = requests.get('http://google.com')
      if response.ok:
          return response.ok
      else:
          return GoogleNotAccessibleError(
                "http request to google.com failed with status code %s" % response.status_code)

   try:
       is_accessible = google_is_accessible()
   except GoogleNotAccessibleError as e:
       is_accessible = False
       print(e.message)

There are pros and cons to the above. We do get back some useful information about the failure.
Unfortunately, we do not get back the response object so we cannot dig deeper into the response
to determine the cause of the error. To get the HTTP status code we have search the error message.

Another drawback is that the raised exception is a side effect that we have to
handle immediately and cannot be deferred until later. Raising an exception also
generates something we don't need, a stacktrace.

One big positive here is that we can subclass exception to indicate the particular problem that
occurred.

Strategy #4 Return a custom Error in case of Failure
------------------------------------------------------

Instead of raising an Exception, you can simply return an `Error` in case of
failure where Error is an object that is an exception or looks a lot like one.
::

  import requests


  class GoogleNotAccessibleError():

      def __init__(self, message, response):
          self.message = message
          self.response = response
  
  def google_is_accessible():
      response = requests.get('http://google.com')
      if response.ok:
          return response.ok
      else:
          return GoogleNotAccessibleError(
                "http request to google.com failed", response)

   result = google_is_accessible()
   if result is True:
       print('It worked!')
   else:
       print(result.message)
       print('HTTP request failed with status code %d' result.value.status_code)

This is a big improvement! We can quickly determine if google is accessible and have
access to all the information in the request. The main drawback to returning a custom
error is that each implementation is likely custom. The calling code has
to know the internals of the returned Error class.


Strategy #5 Return an instance of Success or Failure containing a value
-------------------------------------------------------------------------

This final strategy refines the custom Error with standard semantics. As it turns out there
a standard paradigm in the `Either class <https://www.ibm.com/developerworks/library/j-ft13/index.html>`_ that is present in Clojure, Scala, and other languages. This package
implements the Either class under the name `Try` as your dear author believes it
is a more intuitive name.

The `Try` class has two subclasses, `Success` and `Failure`. Success is used to
contain the result of an operation that-you guessed it-succeeded. Likewise, Failure
contains the result of an operation that failed.

Here is the same task using the ``Success`` and ``Failure``::

  import requests
  from tryme import Success, Failure


  def google_is_accessible():
      response = requests.get('http://google.com')
      if response.ok:
          return Success(response)
      else:
          return Failure(response)

   result = google_is_accessible()
   if result.succeeded():
       print('it worked!')
   else:
       response = result.get_failure()
       print('HTTP request failed with status %d' % response.status_code)

We noted earlier that an advantage of returning exceptions is that we can subclass
Exception to more specifically indicate the failure. We can do the same with
Success in Failure. One obvious omission from our google_is_accessible is
that it does not account for a network failure.::


  import requests
  from tryme import Success, Failure


  class ConnectionFailure(Failure):
      pass
      
  
  def google_is_accessible():
      try:
          response = requests.get('http://google.com')
      except requests.exceptions.ConnectionError as e:
          return ConnectionFailure(e.message)
      if response.ok:
          return Success(response)
      else:
          return Failure(response)

   result = google_is_accessible()
   if result.succeeded():
       print('it worked!')
   elif isinstance(result, ConnectionFailure):
       print(result.get_message())
   else:
       response = result.get_failure()
       print('HTTP request failed with status %d' % response.status_code)


Note that while we return a custom Failure in this case there are many cases where it
is quite reasonable to raise an exception. As mentioned earlier, exceptions work well
for **unexpected** behavior and not expected behavior.

Success and Failure have some useful helpers for reporting to the terminal.

The constructors for both Success and Failure take the optional argument `message`
to capture a message intended for the end user. the `to_console` method prints the
message to the terminal if it is not None otherwise prints a a string representation
of the contained value.

* `Success.to_console` prints the message if set otherwise prints a string representation of
  the contained value to stdout
* `Failure.to_console` prints the message if set otherwise prints a string representation of
  the contained value to stderr
* `Try.raise_for_error` raise an exception if the instance is a Failure
* `Try.fail_for_error` if a Failure, print the message and exit with a non-zero return code

  
Retrying with Style
---------------------------------------------------

Let's say we want to create a single server using a new Cloud computing provider
named HighlyVariable Inc. HighlyVariable can provision our new server in a few
seconds, several minutes, or occasionally not at all. Your dear author has used
cloud services where the "not at all" is not so uncommon an outcome!

Let's create a `server_ready` function that returns a `Success` when the server
is ready, a `Failure` when the operation times out. A "terminal" state such as
"Ready" or "Failed" will terminate retries immediately whereas a Failed will
continue execution of the `server_ready` function until 300 seconds after the
function was first called.

If our new server is not ready after 300 seconds, `server_ready` will return an
instance of `Failure`.

::

   from tryme import retry, Success, Failure

   
   def create_server(name):
       return {'Name': name}

   status_iterator = iter(['Preparing', 'Preparing', 'Preparing', 'Ready'])

   
   def check_instance_status(name):
       return next(status_iterator)

     
   @retry
   def wait_for_server_ready_or_failed(name):
       status = check_instance_status(name)
       if status in ['Ready', 'Failed']:
           return Success(status)
       else:
           return Failure(status)

           
   def server_ready(name):
       # the decorated function will return two values,
       # the result of wrapped function is updated with start and end times of the
       # retry loop and the total count of attempts
       # note that the wrapped value is not modified
       result = wait_for_server_ready_or_failed(name)

       # a failure here only indicates a timeout
       if result.failed():
           return Failure("Server %s not ready after %d seconds and %d attempts"
                          % (name, result.elapsed, result.count))

       # unwrap the value to see what really happened
       status = result.get()
       if status == 'Ready':
           return Success("server %s is ready after %d seconds and %d attempts!"
                          % (name, result.elapsed, result.count))
       else:
           return Failure("server %s failed after %d seconds!"
                          % (name, result.elapsed))

   result = server_ready('jenkins')
   assert result.succeeded()
   print("Server jenkins is ready after %d seconds and %d attempts!"
         % (result.elapsed, result.count))
   
There something a little weird about the above example. Why did we return
Success when the status was "Failed"? This is because the return value of
Failure in the wrapped function is a signal to the `@retry` decorator to
continue retrying until the timeout is reached. As noted earlier, you
can subclass Success and Failure with names that make more sense for your context.
Tryme in fact comes with two subclasses py:class:`Stop` and py:class:`Again`. Let's
refactor the previous example to use them.::

   from tryme import retry, Success, Failure, Stop, Again

   def create_server(name):
       return {'Name': name}

   status_iterator = iter(['Preparing', 'Preparing', 'Preparing', 'Ready'])

   def check_instance_status(name):
       return next(status_iterator)

   @retry
   def wait_for_server_ready_or_failed(name):
       status = check_instance_status(name)
       if status in ['Ready', 'Failed']:
           return Stop(status)
       else:
           return Again(status)

   def server_ready(name):
       # the decorated function will return two values,
       # the result of wrapped function is updated with start and end times of the
       # retry loop and the total count of attempts
       # note that the wrapped value is not modified
       result = wait_for_server_ready_or_failed(name)

       # a failure here only indicates a timeout
       if result.failed():
           return Failure("Server %s not ready after %d seconds and %d attempts"
                          % (name, result.elapsed, result.count))

       # unwrap the value to see what really happened
       status = result.get()
       if status == 'Ready':
           return Success("server %s is ready after %d seconds and %d attempts!"
                          % (name, result.elapsed, result.count))
       else:
           return Failure("server %s failed after %d seconds!"
                          % (name, result.elapsed))

   result = server_ready('jenkins')
   assert result.succeeded()
   print("Server jenkins is ready after %d seconds and %d attempts!"
         % (result.elapsed, result.count))
       
Utility methods
--------------------
       
The utility method ``try_out`` executes a callable and wraps a raised exception
in a Failure class. If an exception was not raised, a Success is returned

::

  >>> from tryme import try_out
  >>> result = try_out(lambda: 1 / 0)
  >>> print(result)  # doctest: +SKIP
  Failure(ZeroDivisionError('integer division or modulo by zero',))
  >>> exc = result.get_failure()
  >>> exc # doctest: +SKIP
  ZeroDivisionError('integer division or modulo by zero',)
  >>> # the following would fail as it does not catch the correct exception, ZeroDivisionError
  >>> # result = try_out(lambda: 1 / 0, exception=ValueError)
  >>> result = try_out(lambda: 1 / 1)
  >>> print(result) # doctest: +SKIP
  Success(1)
  >>> result.get() # doctest: +SKIP
  1




Requirements
============

- CPython >= 2.7


Background
============

This package is inspired by Philip Xu's excellent `monad package <https://github.com/pyx/monad>`_.
It also takes some inspiration from the excellent `vavr <https://vavr.io>`_ library for java and the Scala language.
See this excellent `tutorial <http://danielwestheide.com/blog/2012/12/26/the-neophytes-guide-to-scala-part-6-error-handling-with-try.html>`_
on the Try utility in Scala.

Pssssh! This package uses *gasp* monads as the core abstraction. *Don't tell
anyone!* They will sick the procedural programming police on your dear author. While this
package does have a Monad class, it does not provide general purpose
implementations of monad, applicative, and functor. Further it does not
attempt to overload common Python operators to support function composition. This is
because your dear author is of the opinion that Python's syntax is too limited
to support monadic composition.


Installation
============

Install from PyPI::

  pip install tryme

Install from source, download source package, decompress, then ``cd`` into source directory, run::

  make install


License
=======

BSD New, see LICENSE for details.


Links
=====

Documentation:
  http://tryme.readthedocs.org/

Issue Tracker:
  https://github.com/bryanwb/tryme/issues/

Source Package @ PyPI:
  https://pypi.python.org/bryanwb/tryme

Git Repository @ Github:
  https://github.com/bryanwb/tryme/
