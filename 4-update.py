#!/usr/bin/python3

import os
import subprocess
import sys
from git import Repo

SKIP = ["linuxmint-installation-guide", "mintubiquity", "slideshow-mint"]
XAPP_PROJECTS = ["fingwit", "velocitty", "clockenstein", "xepub", "unfold", "superlight", "gnome-online-accounts-gtk"]
CUSTOM_REMOTES = {"mintchat": "git@gitlab.com:linuxmint/pins/mint/mintchat.git"}
CURR_DIR = os.getcwd()
PO_DIR = os.path.join(CURR_DIR, "po-export")
FOREIGN_DIR = os.path.join(PO_DIR, "FOREIGN")
WORKING_DIR = os.path.expanduser("~/Sandbox/translations/")
os.system("mkdir -p '%s'" % WORKING_DIR)
os.system("rm -rf '%s/*'" % WORKING_DIR)

def notify(message, submessage):
    print(f"""
        ========================================
        {message}
        ========================================

        {submessage}

    """)

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
        notify(repo_name.upper(), "Generate po/LINGUAS...")
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
        notify(repo_name.upper(), "Generating l10n files...")
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
    os.system("gnome-terminal &")
    notify(repo_name.upper(), "Press a key when ready to continue...")
    input()
    os.system(f"rm -rf '{FOREIGN_DIR}/{repo_name}'")

def generate_files(repo_name):
    generate_scripts = []
    for filename in sorted(os.listdir()):
        if filename.startswith("generate_"):
            generate_scripts.append(filename)
    if len(generate_scripts) == 0:
        notify(repo_name.upper(), "No generate_ scripts, skipping.")
        return
    for script in generate_scripts:
        os.system(f"./{script}")
    if subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout == "":
        notify(repo_name.upper(), "No changes, skipping.")
        return
    os.system("git commit -a -m 'l10n: Update files'")
    os.system("git dch")
    os.system("smerge ./")
    os.system("gnome-terminal &")
    notify(repo_name.upper(), "Press a key when ready to continue...")
    input()

# Foreign projects: copy their translations into their repositories
if os.path.exists(FOREIGN_DIR):
    os.chdir(FOREIGN_DIR)
    for project in sorted(os.listdir()):
        if project in SKIP:
            continue
        notify(project.upper(), "Updating translations...")
        clone_or_reset(project, WORKING_DIR)
        copy_translations(project)

# Whatever is left in FOREIGN needs manual work
while os.path.exists(FOREIGN_DIR):
    notify("FOREIGN", "Left in po-export/FOREIGN: %s\n\n        Handle them, remove po-export/FOREIGN and press a key..." % ", ".join(sorted(os.listdir(FOREIGN_DIR))))
    input()

# Build and install mint-translations, the native projects read its .mo files
os.chdir(CURR_DIR)
while True:
    version = subprocess.run(["dpkg-parsechangelog", "-S", "Version"], capture_output=True, text=True).stdout.strip()
    installed = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "mint-translations"], capture_output=True, text=True).stdout.strip()
    if version != installed:
        break
    notify("MINT-TRANSLATIONS", f"Version {version} is already installed. Bump it with dch and press a key...")
    input()
notify("MINT-TRANSLATIONS", f"Building and installing {version}...")
os.system("dpkg-buildpackage -b -us -uc")
if os.system(f"sudo dpkg -i ../mint-translations_{version}_all.deb") != 0:
    sys.exit(f"Could not install mint-translations {version}.")

# Native projects: regenerate the files which use their translations
for project in sorted(os.listdir(PO_DIR)):
    if not os.path.isdir(os.path.join(PO_DIR, project)):
        continue
    notify(project.upper(), "Generating l10n files...")
    clone_or_reset(project, WORKING_DIR)
    generate_files(project)

