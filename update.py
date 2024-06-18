#!/usr/bin/python3

import os
import sys
from git import Repo

SKIP = ["linuxmint-installation-guide", "mintubiquity", "slideshow-mint"]
CURR_DIR = os.getcwd()
FOREIGN_DIR = os.path.join(CURR_DIR, "po-export/FOREIGN")
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

os.chdir(FOREIGN_DIR)
for project in sorted(os.listdir()):
    if project in SKIP:
        continue
    notify(project.upper(), "Updating translations...")
    clone_or_reset(project, WORKING_DIR)
    copy_translations(project)

