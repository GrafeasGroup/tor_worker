import sh
from io import StringIO
from tor_worker import __version__

def test_is_installed():
    cmd_exists = sh.Command('command').bake('-v')
    assert cmd_exists('tor-worker').exit_code == 0

def test_version():
    buf = StringIO()
    sh.tor_worker('--version', _out=buf)

    assert 'tor-worker' in buf.getvalue()

def test_subcommands():
    with StringIO() as buf:
        sh.tor_worker('work', '--help', _out=buf)
        out = buf.getvalue()
        assert 'tor-worker work' in out
