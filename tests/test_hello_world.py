def test_hello_world(capsys):
    print("Hello, world!")
    captured = capsys.readouterr()
    assert "Hello, world!" in captured.out
