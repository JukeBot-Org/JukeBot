from os import system
import os
import sys

in_virtualenv = sys.base_prefix != sys.prefix
site_packages_dir = sys.prefix
pyinstaller_build_command = f"pyinstaller -F --paths={site_packages_dir}  bot.py"
print(f"In virtualenv? {in_virtualenv}")
print(f"using \"{site_packages_dir}\" for site-packages ")
print("Commencing build...")
os.system(pyinstaller_build_command)
