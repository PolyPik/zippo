# zippo

[![PyPI - Version](https://img.shields.io/pypi/v/zippo.svg)](https://pypi.org/project/zippo)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zippo.svg)](https://pypi.org/project/zippo)

-----
A command line tool for creating a ZIP archive of a filesystem directory.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install zippo
```
## Usage

```console
Usage: zippo [OPTIONS] SRC

  This tool creates a zip archive of a filesystem directory.

  SRC is the path to the directory containing the files that need to be
  archived.

Options:
  -r, --root-directory <name>     Sets the name of the archive root directory.
                                  By default, the directory name is that of
                                  SRC.
  -n, --no-root-dir               Disables the use of an archive root
                                  directory.
  -o, --output-file <filepath>    Sets the name of the output file. By
                                  default, the filename is that of SRC with a
                                  ".zip" extension.
  -c, --compression [STORED|DEFLATED|BZIP2|LZMA]
                                  Sets the compression method. By default, the
                                  compression method is "STORED".
  -l, --compress-level [1|2|3|4|5|6|7|8|9]
                                  Sets the level of compression. By default,
                                  the compression level is "1". This option
                                  only has effect if the compression method is
                                  "DEFLATE" or "BZIP2".
  --help                          Show this message and exit.
```

## License

`zippo` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
