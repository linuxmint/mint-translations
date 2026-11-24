#!/usr/bin/python3

import os
import subprocess
import sys
from git import Repo
from rich.console import Console
from rich.markup import escape
from rich.prompt import Prompt

SKIP = ["linuxmint-installation-guide", "mintubiquity", "slideshow-mint"]
XAPP_PROJECTS = ["fingwit", "velocitty", "clockenstein", "xepub", "unfold", "superlight", "gnome-online-accounts-gtk"]
CUSTOM_REMOTES = {"mintchat": "git@gitlab.com:linuxmint/pins/mint/mintchat.git"}
CURR_DIR = os.getcwd()
PO_DIR = os.path.join(CURR_DIR, "po-export")
FOREIGN_DIR = os.path.join(PO_DIR, "FOREIGN")
WORKING_DIR = os.path.expanduser("~/Sandbox/translations/")
os.system("mkdir -p '%s'" % WORKING_DIR)
os.system("rm -rf '%s/*'" % WORKING_DIR)

console = Console(highlight=False)

def title(text):
    console.print()
    console.rule(f"[bold green]{escape(text)}")

def info(text):
    console.print(f"[cyan]{escape(text)}")

def wait(text):
    console.input(f"[bold yellow]{escape(text)}[/] ")

def clone_or_reset(repo_name, parent_path):
    os.chdir(parent_path)
    if os.path.exists(repo_name):
        # clean up repository
        os.chdir(repo_name)
        os.system("git checkout -f")
        os.system("git clean -fd")
        os.system("git checkout master")
        os.system("git pull origin master")
    else:
        # clone repository from github
        if repo_name in CUSTOM_REMOTES:
            os.system("git clone %s" % CUSTOM_REMOTES[repo_name])
        elif repo_name in XAPP_PROJECTS:
            os.system("git clone git@github.com:xapp-project/%s.git" % repo_name)
        else:
            os.system("git clone git@github.com:linuxmint/%s.git" % repo_name)
        os.chdir(repo_name)

def copy_translations(repo_name):
    repo_path = os.path.join(WORKING_DIR, repo_name)
    os.chdir(repo_path)
    os.system(f"cp -R {FOREIGN_DIR}/{repo_name}/*.po {repo_path}/po/")
    repo = Repo(repo_path)
    if os.path.exists("po/LINGUAS"):
        info("Generating po/LINGUAS...")
        os.system("rm po/LINGUAS")
        for filename in sorted(os.listdir("po")):
            if filename.endswith(".po"):
                filename = filename.replace(".po", "")
                os.system(f"echo {filename} >> po/LINGUAS")
    os.system("git add *")
    os.system("git commit -m 'l10n: Update translations'")
    generate_scripts = []
    for filename in os.listdir():
        if filename.startswith("generate_"):
            generate_scripts.append(filename)
    if len(generate_scripts) > 0:
        info("Generating l10n files...")
        os.system("rm -rf ../*.deb")
        os.system("dpkg-buildpackage")
        os.system("git checkout -f")
        os.system("git clean -fd")
        os.system("sudo dpkg -i ../*.deb")
        for script in generate_scripts:
            os.system(f"./{script}")
        os.system("git commit -a -m 'l10n: Update files'")
    os.system("git dch")
    os.system("smerge ./")
    os.system("velocitty &")
    wait("Press Enter when ready to continue...")
    os.system(f"rm -rf '{FOREIGN_DIR}/{repo_name}'")

def generate_files(repo_name):
    generate_scripts = []
    for filename in sorted(os.listdir()):
        if filename.startswith("generate_"):
            generate_scripts.append(filename)
    if len(generate_scripts) == 0:
        info("No generate_ scripts, skipping.")
        return
    info("Generating l10n files...")
    for script in generate_scripts:
        os.system(f"./{script}")
    if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout == "":
        info("No changes, skipping.")
        return
    os.system("git commit -a -m 'l10n: Update files'")
    os.system("git dch")
    os.system("smerge ./")
    os.system("velocitty &")
    wait("Press Enter when ready to continue...")

# Foreign projects: copy their translations into their repositories
if os.path.exists(FOREIGN_DIR):
    projects = [project for project in sorted(os.listdir(FOREIGN_DIR)) if project not in SKIP]
    for index, project in enumerate(projects, start=1):
        title(f"{project} ({index}/{len(projects)})")
        info("Updating translations...")
        clone_or_reset(project, WORKING_DIR)
        copy_translations(project)

# Whatever is left in FOREIGN needs manual work
while os.path.exists(FOREIGN_DIR):
    title("FOREIGN")
    console.print("[bold red]Left in po-export/FOREIGN, needs manual work:")
    for project in sorted(os.listdir(FOREIGN_DIR)):
        console.print(f"  • {escape(project)}")
    wait("Handle them, remove po-export/FOREIGN and press Enter...")

# Build and install mint-translations, the native projects read its .mo files
os.chdir(CURR_DIR)
title("mint-translations")
while True:
    version = subprocess.run(["dpkg-parsechangelog", "-S", "Version"], capture_output=True, text=True).stdout.strip()
    installed = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "mint-translations"], capture_output=True, text=True).stdout.strip()
    if version != installed:
        break
    console.print(f"[bold yellow]Version {escape(version)} is already installed.")
    answer = Prompt.ask("Bump it with dch and retry, or ignore and reinstall it", choices=["retry", "ignore"], default="retry", console=console)
    if answer == "ignore":
        break
info(f"Building and installing {version}...")
os.system("dpkg-buildpackage -b -us -uc")
if os.system(f"sudo dpkg -i ../mint-translations_{version}_all.deb") != 0:
    console.print(f"[bold red]Could not install mint-translations {escape(version)}.")
    sys.exit(1)

# Native projects: regenerate the files which use their translations
projects = [project for project in sorted(os.listdir(PO_DIR)) if os.path.isdir(os.path.join(PO_DIR, project))]
for index, project in enumerate(projects, start=1):
    title(f"{project} ({index}/{len(projects)})")
    clone_or_reset(project, WORKING_DIR)
    generate_files(project)

