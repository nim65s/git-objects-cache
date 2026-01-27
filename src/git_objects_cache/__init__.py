"""
git-objects-cache

A big fetch cache for your git objects
"""

from argparse import ArgumentParser
from os import environ
from logging import getLogger, basicConfig
from subprocess import check_call, check_output
from pathlib import Path

from tomlkit import load, dump

_NAME = "git-objects-cache"
_NAME_UP = "GIT_OBJECTS_CACHE"
_LOG = getLogger(_NAME)


class Config:
    def __init__(self):
        self.conf_dir = Path(
            environ.get(
                f"{_NAME_UP}_CONF_DIR",
                Path(environ.get("XDG_CONFIG_HOME", "~/.config")) / _NAME,
            )
        ).expanduser()
        _LOG.debug("conf dir: '%s'", self.conf_dir)

        if not self.conf_dir.is_dir():
            _LOG.info("creating '%s' directory", self.conf_dir)
            self.conf_dir.mkdir(parents=True)

        self.conf_file = self.conf_dir / "config.toml"
        _LOG.debug("conf file: '%s'", self.conf_file)

        if not self.conf_file.exists():
            _LOG.info("creating '%s' file", self.conf_file)
            self.conf_file.touch()

        with self.conf_file.open() as f:
            self.conf = load(f)

        self.repo = Path(
            self.conf[_NAME]["repo"]
            if _NAME in self.conf and "repo" in self.conf[_NAME]
            else environ.get(
                f"{_NAME_UP}_REPO",
                Path(environ.get("XDG_CACHE_HOME", "~/.cache")) / _NAME,
            )
        ).expanduser()
        _LOG.debug("repo: '%s'", self.repo)

        if "remotes" not in self.conf:
            self.conf["remotes"] = {}
        if _NAME not in self.conf:
            self.conf[_NAME] = {}
        if "repo" not in self.conf[_NAME]:
            _LOG.debug("adding repo to conf")
            self.conf[_NAME]["repo"] = str(self.repo.absolute())
            with self.conf_file.open("w") as f:
                dump(self.conf, f, sort_keys=True)

        if not self.repo.is_dir():
            _LOG.info("creating '%s' repo", self.repo)
            self.repo.mkdir(parents=True)
            check_call(["git", "init", "--bare"], cwd=self.repo)

        template = self.conf_dir / "template"
        info = template / "objects" / "info"
        if not info.is_dir():
            _LOG.info("creating '%s' template", template)
            info.mkdir(parents=True)
            with (info / "alternates").open("w") as f:
                print((self.repo / "objects").absolute(), file=f)
            check_call(["git", "config", "--global", "init.templateDir", template])


def parse_args():
    parser = ArgumentParser(prog="git objects-cache", description=__doc__)

    parser.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=int(environ.get("QUIET", 0)),
        help="decrement verbosity level",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=int(environ.get("VERBOSITY", 0)),
        help="increment verbosity level",
    )

    parser.add_argument(
        "-f", "--fast", action="store_true", help="don't update remotes before fetching"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    basicConfig(level=30 - 10 * args.verbose + 10 * args.quiet)

    _LOG.info("init...")

    config = Config()

    if not args.fast:
        _LOG.info("sync remotes with config file...")
        remotes_list = check_output(
            ["git", "remote", "-v"], text=True, cwd=config.repo
        ).strip()
        remotes = (
            dict(
                r.removesuffix(" (fetch)").removesuffix(" (push)").split("\t")
                for r in remotes_list.split("\n")
            )
            if remotes_list
            else {}
        )

        for name, url in remotes.items():
            if name not in config.conf["remotes"]:
                _LOG.warning("removing '%s' remote to '%s'", name, url)
                check_call(["git", "remote", "remove", name], cwd=config.repo)

        for name, url in config.conf["remotes"].items():
            if name not in remotes:
                _LOG.info("adding '%s' remote to '%s'", name, url)
                check_call(
                    ["git", "remote", "add", "--no-tags", name, url], cwd=config.repo
                )
            elif remotes[name] != url:
                _LOG.info(
                    "updating '%s' remote from '%s' to '%s'", name, remotes[name], url
                )
                check_call(["git", "remote", "set-url", name, url], cwd=config.repo)

    _LOG.info("updating cache...")
    check_call(["git", "fetch", "--all", "--no-tags", "--prune"], cwd=config.repo)
    _LOG.debug("done.")
