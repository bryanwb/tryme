from tryme.tryme import retry, Success, Failure
from tryme import tryme
import pytest


def test_retry_simple(capsys):
    @retry
    def always_true():
        return tryme.Success('it worked!')

    log, result = always_true()
    assert log.start != log.end
    assert log.count == 1
    assert log.elapsed == log.end - log.start
    assert result.succeeded()

    def also_true():
        return tryme.Success('it worked!')

    decorated_also_true = retry(also_true)
    log, result = decorated_also_true()
    assert log.start != log.end
    assert log.count == 1
    assert log.elapsed == log.end - log.start
    assert result.succeeded()

    # # retry should be silent by default
    stdout, stderr = capsys.readouterr()
    assert stdout == '' and stderr == ''


def test_retry_timeout(stopped_clock):
    stopped_clock.set_times([0, 100, 200, 300, 400])
    
    @retry
    def never_true():
        return tryme.Failure('It failed!')

    log, result = never_true()
    assert log.start != log.end
    assert log.count == 3
    assert log.elapsed == log.end - log.start
    assert result.failed()

    
def test_retry_success_after_3_tries(stopped_clock):
    stopped_clock.set_times([0, 400, 800, 900, 950])

    success_iterator = iter([Failure('failed!'), Failure('failed!'), Success('success!')])
    
    @retry(timeout=1000)
    def success_on_3rd_attempt():
        return success_iterator.next()

    log, result = success_on_3rd_attempt()
    assert log.start != log.end
    assert log.count == 3
    assert log.elapsed == 900
    assert result.succeeded()


def test_retry_fail_invalid_return_values():
    def invalid_return_values():
        return False

    with pytest.raises(tryme.InvalidCallableError):
        retry(invalid_return_values)()


def test_retry_logging_callback(capsys, stopped_clock):
    stopped_clock.set_times([0, 100, 200, 300, 400])
    
    def logging_callback(log):
        print("Retrying after %d seconds and %d attempts" % (log.elapsed, log.count))
    
    success_iterator = iter([Failure('failed!'), Failure('failed!'), Success('success!')])
    
    @retry(status_callback=logging_callback)
    def success_on_3rd_attempt():
        return success_iterator.next()

    _, _ = success_on_3rd_attempt()
    stdout, stderr = capsys.readouterr()

    lines = stdout.strip().split('\n')
    assert len(lines) >= 3
    for l in lines:
        assert 'Retrying after' in l
    

def test_retry_progress_ticks_80_per_column(capsys, stopped_clock):
    failure_iterator = iter([Failure('failed!') for i in range(0, 200)])
    stopped_clock.set_times(range(0, 100))

    @retry(status_callback=tryme.tick_counter(), timeout=90)
    def this_will_timeout():
        return failure_iterator.next()

    _, result = this_will_timeout()
    stdout, stderr = capsys.readouterr()
    
    assert result.failed()
    first_line = stdout.strip().split('\n')[0]
    assert first_line == ''.join(['.' for i in range(0, 80)])


@pytest.fixture
def stopped_clock(request):
    tryme._clock = tryme.StoppedClock()

    def fin():
        tryme._clock = tryme.SystemClock()
        
    request.addfinalizer(fin)
    
    return tryme._clock
