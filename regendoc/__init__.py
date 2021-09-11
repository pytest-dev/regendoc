import os

import click
import tempfile
from pathlib import Path
from .parse import parse_actions, correct_content
from .actions import ACTIONS
from .substitute import SubstituteRegex, default_substituters


def normalize_content(content, operators):
    lines = content.splitlines(True)
    result = []
    for line in lines:
        for op in operators:
            line = op(line)
        result.append(line)
    return "".join(result)


def check_file(name, content, tmp_dir: Path, normalize, verbose: bool = True):
    needed_updates = []
    for action in parse_actions(content, file=name):
        method = ACTIONS[action["action"]]
        new_content = method(
            name=name, target_dir=tmp_dir, action=action, verbose=verbose
        )
        if new_content:
            action["new_content"] = normalize_content(new_content, normalize)
            needed_updates.append(action)
    return needed_updates


def print_diff(action):
    content, out = action["content"], action["new_content"]
    if out != content:
        import difflib

        differ = difflib.Differ()
        outl = out.splitlines(True)
        contl = content.splitlines(True)
        lines = differ.compare(contl, outl)

        mapping = {"+": "green", "-": "red", "?": "blue"}
        if lines:
            click.secho("$ " + action["target"], bold=True, fg="blue")
        for line in lines:
            color = mapping.get(line[0])
            if color:
                click.secho(line, fg=color, bold=True, nl=False)
            else:
                click.echo(line, nl=False)


def mktemp(rootdir, name):
    if rootdir is not None:
        return Path(rootdir)
    root = tempfile.gettempdir()
    rootdir = Path(root, "regendoc-tmpdirs")
    rootdir.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=name + "-", dir=rootdir))


@click.command()
@click.argument("files", nargs=-1)
@click.option("--update", is_flag=True)
@click.option("--normalize", type=SubstituteRegex.parse, multiple=True)
@click.option("--verbose", default=False, is_flag=True)
def main(files, update, normalize=(), rootdir=None, def_name=None, verbose=False):
    cwd = Path.cwd()
    verbose = True
    tmpdir: Path = mktemp(rootdir, cwd.name)
    total = len(files)
    for num, name in enumerate(files, 1):
        targetdir = tmpdir.joinpath("%s-%d" % (os.path.basename(name), num))
        with open(name) as fp:
            content = list(fp)
        targetdir.mkdir()
        click.secho(
            f"#[{num:3d}/{total:3d}] {name}",
            bold=True,
        )
        updates = check_file(
            name=name,
            content=content,
            tmp_dir=targetdir,
            normalize=default_substituters(targetdir) + list(normalize),
            verbose=verbose,
        )
        for action in updates:
            if action["content"] is None or action["new_content"] is None:
                continue

            print_diff(action)
        if update:
            corrected = correct_content(content, updates)
            with open(name, "w", encoding="UTF-8") as f:
                f.writelines(corrected)
