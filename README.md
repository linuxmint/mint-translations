1. Download POs from Launchpad
2. Replace the content po-export with the content of archive downloaded
3. Run ./1-clean.sh
4. Run ./2-check.sh
5. Run ./3-sort.sh to move foreign translations to FOREIGN/
6. Run ./4-update.py to update the foreign projects, build and install
   mint-translations, and update the native projects
