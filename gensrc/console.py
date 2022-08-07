"""
A command-line source code file generator.

Copyright (C) Kevin Morris <kevr@0cost.org>
All Rights Reserved.
"""
import argparse
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Tuple

import jinja2
import pygit2

PROG = "gensrc"
GITHUB = f"https://github.com/kevr/{PROG}"

TYPES = ("main",)

SUPPORTED = [
    "cpp",
    "py",
]

logging.basicConfig()
logger = logging.getLogger("gensrc")


def error(*args, **kwargs):
    logger.error(*args, **kwargs)
    return 1


def parse_args():
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument("type", choices=TYPES)
    parser.add_argument("-o", "--output", dest="output", required=True)
    parser.add_argument("-f", "--force", default=False,
                        action="store_const", const=True)
    return parser.parse_args()


def git_config() -> Tuple[str]:
    config = pygit2.Config.get_global_config()

    return (
        config["user.name"],
        config["user.email"]
    )


def main():
    args = parse_args()

    try:
        real_name, email = git_config()
    except KeyError:
        return error("your global Git config must contain both "
                     "user.name and user.email.\n"
                     "\nTo set your name: "
                     "\n    $ git config --global user.name 'John Doe'"
                     "\nTo set your email: "
                     "\n    $ git config --global user.email 'john@doe.com'\n")

    output = args.output
    if not args.force and os.path.exists(output):
        return error(f"file already exists: {output}")

    extension = None
    pieces = output.split(".")
    if len(pieces) < 2:
        return error("supported language extension is required, "
                     f"supported extensions: {', '.join(SUPPORTED)}")

    extension = pieces[-1]

    template_type = args.type
    if extension:
        logger.info("language selected based on output: {extension}")
        template_type = f"{template_type}.{extension}"

    env = jinja2.Environment(
        loader=jinja2.PackageLoader("gensrc", "templates")
    )

    template_name = f"{template_type}.j2"

    try:
        template = env.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        return error(f"invalid language extension used: {extension}; "
                     f"supported extensions: {', '.join(SUPPORTED)}")

    content = template.render(
        year=datetime.now().year,
        author=f"{real_name} <{email}>"
    )

    with open(output, "w") as f:
        f.write(content)

    return 0


def run():
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        print()
        error("If you believe this is a bug, please report its entire\n"
              f"output as an issue on {GITHUB} with the command used")


if __name__ == "__main__":
    run()
