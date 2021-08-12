# -*- coding: utf-8 -*-

import json
import os
from textwrap import dedent

import click

from plugin import (
    ICON_PATH,
    PLUGIN_ACTION_KEYWORD,
    PLUGIN_AUTHOR,
    PLUGIN_EXECUTE_FILENAME,
    PLUGIN_ID,
    PLUGIN_PROGRAM_LANG,
    PLUGIN_URL,
    __long_description__,
    __package_name__,
    __short_description__,
    __version__,
    basedir,
)


@click.group()
def translate():
    """Translation and localization commands."""
    ...


@translate.command()
@click.argument("locale")
def init(locale):
    """Initialize a new language."""

    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("extract command failed")
    if os.system(f"pybabel init -i messages.pot -d plugin/translations -l {locale}"):
        raise RuntimeError("init command failed")
    os.remove("messages.pot")

    click.echo("Done.")


@translate.command()
def update():
    """Update all languages."""
    if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
        raise RuntimeError("extract command failed")
    if os.system("pybabel update -i messages.pot -d plugin/translations"):
        raise RuntimeError("update command failed")
    os.remove("messages.pot")

    click.echo("Done.")


@translate.command()
def compile():
    """Compile all languages."""

    if os.system("pybabel compile -d plugin/translations"):
        raise RuntimeError("compile command failed")

    click.echo("Done.")


@click.group()
def plugin():
    """Plugin commands."""
    ...


@plugin.command()
def install_dependencies():
    """Install dependencies to local."""

    lib_path = basedir / "lib"
    os.system(f"pip install -r requirements.txt -t {lib_path} --upgrade")

    click.echo("Done.")

@plugin.command()
def setup_dev_env():
    """Set up the development environment for the first time. This installs requirements-dev.txt """

    os.system(f"pip install -r requirements-dev.txt --upgrade")

    click.echo("Dev environment ready to go.")

@plugin.command()
def gen_plugin_info():
    """Auto generate the 'plugin.json' file for Flow."""

    plugin_infos = {
        "ID": PLUGIN_ID,
        "ActionKeyword": PLUGIN_ACTION_KEYWORD,
        "Name": __package_name__.title(),
        "Description": __short_description__,
        "Author": PLUGIN_AUTHOR,
        "Version": __version__,
        "Language": PLUGIN_PROGRAM_LANG,
        "Website": PLUGIN_URL,
        "IcoPath": ICON_PATH,
        "ExecuteFileName": PLUGIN_EXECUTE_FILENAME,
    }

    with open(basedir / "plugin.json", "w") as f:
        json.dump(plugin_infos, f, indent=4)

    click.echo("Done.")


@plugin.command()
def build():
    "Pack plugin to a zip file."

    # zip plugin
    build_path = basedir / "build"
    build_path.mkdir(exist_ok=True)
    zip_path = build_path / f"{__package_name__.title()}-{__version__}.zip"
    zip_path.unlink(missing_ok=True)

    ignore_list = [
        # folder
        ".git/*",
        ".vscode/*",
        ".history/*",
        "*/__pycache__/*",
        "build/*",
        # file
        ".gitignore",
        ".gitattributes",
    ]
    os.system(f"zip -r {zip_path} . -x {' '.join(ignore_list)}")

    # hook lib folder path to python system environment variable path
    env_snippet = dedent(
        """\
    import os
    import sys

    basedir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(basedir, "lib"))
    """
    )

    entry_src = basedir / "main.py"
    entry_src_temp = build_path / "main.py"
    with open(entry_src, "r") as f_r:
        with open(entry_src_temp, "w", encoding="utf-8") as f_w:
            f_w.write(env_snippet + f_r.read())

    os.system(f"zip -j {zip_path} {entry_src_temp}")
    entry_src_temp.unlink()

    click.echo("Done.")


@click.group()
def clean():
    """Clean commands."""
    ...


@clean.command()
def clean_build():
    """Remove build artifacts"""

    os.system("rm -fr build/")
    click.echo("Done.")


@clean.command()
def clean_pyc():
    "Remove Python file artifacts"

    os.system(f"find {basedir} -name '*.pyc' -exec rm -f {{}} +")
    os.system(f"find {basedir} -name '*.pyo' -exec rm -f {{}} +")
    os.system(f"find {basedir} -name '*~' -exec rm -f {{}} +")

    click.echo("Done.")


if __name__ == "__main__":
    cli = click.CommandCollection(
        sources=[
            clean,
            plugin,
            translate,
        ]
    )
    cli()
