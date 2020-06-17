1. Download POs from Launchpad
2. Replace the content po-export with the content of archive downloaded
3. Run ./clean.sh
4. Run ./check.sh
5. Run ./sort.sh to move foreign translations to FOREIGN/
6. Export foreign translations to other projects
7. Build the package with dpkg-buildpackage
