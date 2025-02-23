import copy
import zipfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from zippo.__main__ import zippo


@pytest.fixture(scope="session")
def src_tree():
    return {
        "foo": {
            "bar.txt": None,
            "fee": {"beer.txt": None, "phy.txt": None},
            "too": {"gar.txt": None, "par.txt": None, "boo": {"wee.txt": None, "woo.txt": None, "whoa.txt": None}},
        }
    }


@pytest.fixture(scope="session")
def base_dir(tmp_path_factory):
    return tmp_path_factory.getbasetemp()


@pytest.fixture(scope="session")
def src_dir(base_dir, src_tree):
    def process_dirtree(root, dir_dict: dict):
        for k, v in dir_dict.items():
            p = root / k
            if v is None:
                p.touch()
            elif isinstance(v, dict):
                p.mkdir()
                process_dirtree(p, v)

    process_dirtree(base_dir, src_tree)

    return base_dir / next(iter(src_tree.keys()))


def make_expected_filenames(src_directory_tree):
    def process_dirtree(parent, dir_dict: dict):
        fp = []
        for k, v in dir_dict.items():
            if v is None:
                p = parent + k
                fp.append(p)
            elif isinstance(v, dict):
                p = (k + "/" if k is not None else "") if parent == "" else parent + k + "/"
                fp.append(p)
                fp.extend(process_dirtree(p, v))

        return fp

    return process_dirtree("", src_directory_tree)


@pytest.mark.parametrize(
    "root_directory",
    [None, "-r", "--root-directory"],
    ids=["Default Root", "Custom Root Short Opt", "Custom Root Long Opt"],
)
@pytest.mark.parametrize(
    "no_root_dir", [None, "-n", "--no-root-dir"], ids=["Has Root", "No Root Short Opt", "No Root Long Opt"]
)
def test_root_dir(base_dir, src_dir, src_tree, root_directory, no_root_dir):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=base_dir) as td:
        args = []

        if root_directory:
            args.extend([root_directory, "car"])

        if no_root_dir:
            args.append(no_root_dir)

        src_tree_copy = copy.deepcopy(src_tree)

        if root_directory or no_root_dir:
            new_root = "car" if not no_root_dir else None
            k = next(iter(src_tree_copy.keys()))
            src_tree_copy[new_root] = src_tree_copy.pop(k)

        args.append(str(src_dir.resolve()))

        result = runner.invoke(zippo, args)
        assert result.exit_code == 0

        zip_file_path = Path(td) / "foo.zip"
        assert zip_file_path.exists()

        expected_filenames = make_expected_filenames(src_tree_copy)

        with zipfile.ZipFile(zip_file_path, "r") as zf:
            for info in zf.infolist():
                assert info.filename in expected_filenames


@pytest.mark.parametrize(
    "output_file",
    [None, "-o", "--output-file"],
    ids=["No Opt", "Short Opt", "Long Opt"],
)
def test_output_file(base_dir, src_dir, output_file):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=base_dir) as td:
        args = []

        if output_file:
            args.extend([output_file, "pin"])

        args.append(str(src_dir.resolve()))

        result = runner.invoke(zippo, args)
        assert result.exit_code == 0

        zip_file_path = Path(td) / ("pin.zip" if output_file else "foo.zip")
        assert zip_file_path.exists()


@pytest.mark.parametrize(
    "compression",
    [
        None,
        "-c STORED",
        "--compression STORED",
        "-c DEFLATED",
        "--compression DEFLATED",
        "-c BZIP2",
        "--compression BZIP2",
        "-c LZMA",
        "--compression LZMA",
    ],
    ids=[
        "No Opt",
        "Short Opt STORED",
        "Long Opt STORED",
        "Short Opt DEFLATED",
        "Long Opt DEFLATED",
        "Short Opt BZIP2",
        "Long Opt BZIP2",
        "Short Opt LZMA",
        "Long Opt LZMA",
    ],
)
def test_compression(base_dir, src_dir, compression):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=base_dir) as td:
        args = []

        expected_method = zipfile.ZIP_STORED
        if compression:
            tokens = compression.split(" ")
            args.extend(list(tokens))
            expected_method = getattr(zipfile, f"ZIP_{tokens[1]}")

        args.append(str(src_dir.resolve()))

        result = runner.invoke(zippo, args)
        assert result.exit_code == 0

        zip_file_path = Path(td) / "foo.zip"
        assert zip_file_path.exists()

        with zipfile.ZipFile(zip_file_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    assert info.compress_type == zipfile.ZIP_STORED
                else:
                    assert info.compress_type == expected_method
