import sh

def test_is_installed():
    cmd_exists = sh.Command('command').bake('-v')
    assert cmd_exists('tor-worker').exit_code == 0
