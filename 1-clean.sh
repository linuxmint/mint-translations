#!/usr/bin/python3

import os

from rich.console import Console
from rich.markup import escape

console = Console(highlight=False)

os.chdir("po-export")

# Remove templates
os.system("rm -f */*.pot")

# remove forbidden locales: pt_PT, fr_FR.
FORBIDDEN_LOCALES = ["fr_FR", "pt_PT", "de_DE"]
for locale in FORBIDDEN_LOCALES:
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('%s.po' % locale):
                fullpath = os.path.join(root, file)
                console.print(f"[red]Deleted[/red] {escape(fullpath)} (forbidden locale)")
                os.unlink(fullpath)

WEIRD_CHARACTERS = {}
WEIRD_CHARACTERS["[nnbsp]"] = " " # U+202F NARROW NO-BREAK SPACE
WEIRD_CHARACTERS["&nnbsp"] = " " # U+202F NARROW NO-BREAK SPACE
WEIRD_CHARACTERS["[nbsp]"] = " " # space character
WEIRD_CHARACTERS["&nbsp"] = " " # space character

# replace weird characters with proper unicode
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith('.po'):
            path = os.path.join(root, file)
            found_weird_character = False
            with open(path) as fh:
                content = fh.read()
                for character in WEIRD_CHARACTERS.keys():
                    if character in content:
                        found_weird_character = True
                        content = content.replace(character, WEIRD_CHARACTERS[character])
            if found_weird_character:
                console.print(f"[yellow]Fixed weird characters in[/yellow] {escape(path)}")
                with open(path, "w") as fh:
                    fh.write(content)
