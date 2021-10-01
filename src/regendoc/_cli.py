from pathlib import Path

from typing import List, Optional, Union
import typer
from . import run
from .substitute import SubstituteRegex, SubstituteAddress

app = typer.Typer()


@app.command()
def typer_main(
    files: List[Path],
    update: bool = typer.Option(False, "--update"),
    normalize: List[str] = typer.Option(default=[]),
    rootdir: Optional[Path] = None,
    def_name: Optional[str] = None,
    verbose: bool = typer.Option(False, "--verbose"),
    columns: Optional[int] = None,
) -> None:

    parsed_normalize: List[Union[SubstituteRegex, SubstituteAddress]] = [
        SubstituteRegex.parse(s) for s in normalize
    ]
    run(
        files=files,
        update=update,
        normalize=parsed_normalize,
        rootdir=rootdir,
        def_name=def_name,
        verbose=verbose,
        columns=columns,
    )
