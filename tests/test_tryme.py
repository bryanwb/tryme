from tryme import tryme
from tryme.tryme import Success, Failure, Some, Nothing
import os
import pytest


def test_try_bool():
    assert Success('it worked!')
    assert not(Failure('it failed!'))


def test_try_comparisons():
    s0 = Success(0)
    s1 = Success(1)
    f0 = Failure(0)
    f1 = Failure(1)

    assert s0 < s1
    assert s1 > s0
    assert s0 == Success(0)
    assert s0 > f0 and s0 > f1
    assert f0 < f1
    assert f0 == Failure(0)
    assert f1 > f0
    

def test_try_get():
    assert Success(0).get() == 0
    with pytest.raises(tryme.NoSuchElementError):
        Failure(0).get()

    assert Failure(0).get_failure() == 0
    with pytest.raises(tryme.NoSuchElementError):
        Success(0).get_failure()


def test_try_message():
    assert Failure(0).get_message() == '0'
    assert Failure(0, message="fubar").get_message() == "fubar"

    assert Success(1).get_message() == '1'
    assert Success(1, message="ok").get_message() == "ok"

    f = Failure(0, message="fubar").set_message('0mfg')
    assert f.get_message() == '0mfg'

    
def test_try_map():
    inc = lambda n: n + 1
    result = Success(0).map(inc)
    assert isinstance(result, Success)
    assert result.get() == 1

    result = Failure(0).map(inc)
    assert isinstance(result, Failure)
    assert result.get_failure() == 0


def test_try_map_failure():
    inc = lambda n: n + 1
    result = Success(0).map_failure(inc)
    assert isinstance(result, Success)
    assert result.get() == 0

    result = Failure(0).map_failure(inc)
    assert isinstance(result, Failure)
    assert result.get_failure() == 1


def test_try_failed_succeeded():
    assert Success(0).succeeded()
    assert not(Success(0).failed())

    assert Failure(0).failed()
    assert not(Failure(0).succeeded())


def test_try_get_or_else():
    assert Success(0).get_or_else(1) == 0
    assert Failure(0).get_or_else(1) == 1


def test_try_out():
    result = tryme.try_out(lambda: 1 / 0)
    assert result.failed()
    assert isinstance(result.get_failure(), ZeroDivisionError)

    with pytest.raises(ZeroDivisionError):
        tryme.try_out(lambda: 1 / 0, exception=ValueError)


def test_try_to_console(capsys):
    success_message = 'It worked!'
    Success(success_message).to_console()
    stdout, stderr = capsys.readouterr()
    assert stdout == success_message + os.linesep
    assert stderr == ''

    Success(success_message).to_console(nl=False)
    stdout, stderr = capsys.readouterr()
    assert stdout == success_message

    failure_message = 'It failed!'
    Failure(failure_message).to_console()
    stdout, stderr = capsys.readouterr()
    assert stderr == failure_message + os.linesep
    assert stdout == ''

    with pytest.raises(SystemExit) as sys_exit:
        Failure(failure_message).to_console(exit_err=True)
        assert sys_exit.value.code == 1

    # test using a custom exit status
    with pytest.raises(SystemExit) as sys_exit:
        Failure(failure_message).to_console(exit_err=True, exit_status=6)
        assert sys_exit.value.code == 6


def test_try_fail_for_error(capsys):
    # no SystemExit should be raised
    assert Success('It worked!').fail_for_error() is None
    stdout, stderr = capsys.readouterr()
    assert stdout == '' and stderr == ''

    failure_message = 'It failed!'
    with pytest.raises(SystemExit):
        Failure(failure_message).fail_for_error()
    stdout, stderr = capsys.readouterr()
    assert stderr == failure_message + os.linesep
    assert stdout == ''

    with pytest.raises(SystemExit) as sys_exit:
        Failure(failure_message).fail_for_error(exit_status=6)
        assert sys_exit.value.code == 1
    

def test_try_raise():
    s = Success(0)
    try:
        s.raise_for_error()
        assert True
    except Exception:
        assert False, "raise_for_error should have no effect for a Success"

    failure_message = 'it failed!'
    f = Failure(failure_message)
    try:
        f.raise_for_error()
        assert False, "raise_for_error should raise an exception for a Failure"        
    except tryme.FailureError as e:
        assert e.message == failure_message

    failure_message = 'it failed!'
    f = Failure(RuntimeError(failure_message))
    try:
        f.raise_for_error()
        assert False, "raise_for_error should raise a RuntimeError when RuntimeError is the original argument"        
    except RuntimeError as e:
        assert e.message == failure_message

    failure_message = 'it failed!'
    f = Failure(failure_message)
    try:
        f.raise_for_error(exception=RuntimeError)
        assert False, "raise_for_error should raise a RuntimeError when RuntimeError is the original argument"        
    except RuntimeError as e:
        assert str(e) == failure_message


def test_try_filter():
    is_even = lambda n: n % 2 == 0

    s0 = Success(2)
    assert s0.filter(is_even).succeeded()
    s1 = Success(1)
    assert s1.filter(is_even).failed()

    assert Failure(1).filter(is_even).failed()


def test_maybe_bool():
    assert Some('it worked!')
    assert not(Nothing)


def test_maybe_comparisons():
    s0 = Some(0)
    s1 = Some(1)

    assert s0 < s1
    assert s1 > s0
    assert s0 == Some(0)
    

def test_maybe_get():
    assert Some(0).get() == 0
    with pytest.raises(tryme.NoSuchElementError):
        Nothing.get()


def test_maybe_map():
    inc = lambda n: n + 1
    result = Some(0).map(inc)
    assert isinstance(result, Some)
    assert result.get() == 1

    result = Nothing.map(inc)
    assert result == Nothing


def test_maybe_is_empty():
    assert Some(0).is_empty() is False
    assert Nothing.is_empty()


def test_maybe_get_or_else():
    assert Some(0).get_or_else(1) == 0
    assert Nothing.get_or_else(1) == 1


def test_maybe_filter():
    is_even = lambda n: n % 2 == 0

    assert Some(0).filter(is_even).get() == 0
    assert Some(1).filter(is_even).is_empty()
