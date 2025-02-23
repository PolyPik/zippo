import zipfile
from pathlib import Path, PurePath

import click


@click.command()
@click.argument("src", type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path))
@click.option(
    "-r",
    "--root-directory",
    default=None,
    metavar="<name>",
    help="Sets the name of the archive root directory. By default, the directory name is that of SRC.",
)
@click.option(
    "-n",
    "--no-root-dir",
    is_flag=True,
    help="Disables the use of an archive root directory.",
)
@click.option(
    "-o",
    "--output-file",
    default=None,
    metavar="<filepath>",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
    help='Sets the name of the output file. By default, the filename is that of SRC with a ".zip" extension.',
)
@click.option(
    "-c",
    "--compression",
    default="STORED",
    type=click.Choice(["STORED", "DEFLATED", "BZIP2", "LZMA"], case_sensitive=False),
    callback=lambda _c, _p, v: getattr(zipfile, f"ZIP_{v}"),
    help='Sets the compression method. By default, the compression method is "STORED".',
)
@click.option(
    "-l",
    "--compress-level",
    default="1",
    type=click.Choice(["1", "2", "3", "4", "5", "6", "7", "8", "9"], case_sensitive=False),
    callback=lambda _c, _p, v: int(v),
    help="""Sets the level of compression. By default, the compression level is "1".
    This option only has effect if the compression method is "DEFLATED" or "BZIP2".""",
)
def zippo(
    src: Path, root_directory: str, output_file: Path, compression: int, compress_level: int, *, no_root_dir: bool
):
    """
    A tool for creating a zipfile from a directory.

    SRC is the path to the directory containing the files that need to be archived.
    """
    file_mappings = {}

    if no_root_dir:
        root_directory = ""
    elif root_directory is None:
        root_directory = src.stem

    for root, _, files in src.walk():
        for f in files:
            arc_path = PurePath(root_directory) / root.relative_to(src) / f
            src_path = root / f
            file_mappings[arc_path] = src_path

    if output_file is None:
        output_file = Path(src.stem)

    output_file = output_file.with_suffix(".zip")

    with zipfile.ZipFile(output_file.resolve(), mode="w", compression=compression, compresslevel=compress_level) as zf:
        for arc_path, src_path in file_mappings.items():
            for parent in [f"{p.as_posix()}/" for p in arc_path.parents[:-1]]:
                if parent not in zf.namelist():
                    zf.mkdir(parent)

            zf.write(src_path.resolve(), arcname=arc_path)


if __name__ == "__main__":
    zippo()
