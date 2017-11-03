#!/usr/bin/python3

import os

os.chdir("po-export")

os.system("mkdir -p FOREIGN/cinnamon-translations")

# special case, xedit -> xed
if os.path.exists("xedit") and os.path.exists("xed"):
	os.system("mv xedit/* xed/")
	os.system("rm -rf xedit")

# cinnamon-translations
for project in ["cinnamon", "cinnamon-bluetooth", "cinnamon-control-center", "cinnamon-session", "cinnamon-settings-daemon", "cinnamon-screensaver", "nemo", "nemo-extensions"]:
	if os.path.exists(project):
		os.system("mv %s FOREIGN/cinnamon-translations/" % project)

# individual projects
for project in ["blueberry", "lightdm-settings", "mdm", "nemo-emblems", "folder-color-switcher", "pix", "xed", "xplayer", "xreader", "xviewer", "slick-greeter", "slideshow-mint", "slideshow-mint-kde"]:
	if os.path.exists(project):
		os.system("mv %s FOREIGN/" % project)

# projects which require locale.po, as opposed to project-locale.po filenames
for project in ["folder-color-switcher", "mdm", "pix", "xed", "xplayer", "xreader", "xviewer", "slick-greeter", "slideshow-mint", "slideshow-mint-kde"]:
	if os.path.exists("FOREIGN/%s" % project):
		os.system("rename 's/%s-//' FOREIGN/%s/*.po" % (project, project))

# mdm requires mo files instead of po files
if os.path.exists("FOREIGN/mdm"):
	os.system("mkdir -p FOREIGN/mdm/launchpad-po")
	for file in os.listdir("FOREIGN/mdm"):
		if file.endswith(".po"):
			locale = file.split(".")[0]
			locale = locale.replace("mdm-", "")
			os.system("mkdir -p FOREIGN/mdm/files/usr/share/mdm/locale/%s/LC_MESSAGES/" % locale)
			os.system("msgfmt -o FOREIGN/mdm/files/usr/share/mdm/locale/%s/LC_MESSAGES/mdm.mo FOREIGN/mdm/%s" % (locale, file))
		if file.endswith(".po") or file.endswith(".pot"):
			os.system("mv FOREIGN/mdm/%s FOREIGN/mdm/launchpad-po/" % file)
