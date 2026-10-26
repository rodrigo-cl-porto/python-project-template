import importlib


def test_package_is_importable():
    package = importlib.import_module("my_awesome_project")

    assert package.__name__ == "my_awesome_project"
