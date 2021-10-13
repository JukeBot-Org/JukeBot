#!/usr/bin/env python3
"""Uses PyInstaller to bundle a single executable file for release. Also
copies over a blank config.json from config.EXAMPLES.json.
When run on Windows this will generate a Windows .EXE file, On Linux a Linux
binary, and on macOS a macOS package (still to be tested, contributions
welcome!)
"""
import os
import sys
import git
from shutil import copy

import PyInstaller.__main__
import colorama
from colorama import Fore as fg
from colorama import Style as st
colorama.init()

def build():
    repo = git.Repo(search_parent_directories=True)
    JukeBot_version = repo.head.object.hexsha[0:7]
    misc_commands_py = "misc_commands.py"

    print(f"{fg.YELLOW}Updating build version in {misc_commands_py}...{st.RESET_ALL}")
    with open(misc_commands_py, "rb+") as filehandle:
        filehandle.seek(-5, os.SEEK_END)
        filehandle.truncate()
    with open(misc_commands_py, "a") as filehandle:
        filehandle.write(f"\"{JukeBot_version}\"\n")

    in_virtualenv = sys.base_prefix != sys.prefix
    site_packages_dir = sys.prefix
    print(f"{fg.YELLOW}In virtualenv? {in_virtualenv}{st.RESET_ALL}")
    print(f"{fg.YELLOW}Using \"{site_packages_dir}\" for site-packages{st.RESET_ALL}")

    print(f"{fg.GREEN}Commencing build...{st.RESET_ALL}")
    PyInstaller.__main__.run([
        "bot.py",
        "--onefile",
        f"--paths={site_packages_dir}",
        f"--name=JukeBot-v.{JukeBot_version}-{sys.platform}"
    ])

    print(f"{fg.YELLOW}Reverting build version in {misc_commands_py}...{st.RESET_ALL}")
    with open(misc_commands_py, "rb+") as filehandle:
        filehandle.seek(-10, os.SEEK_END)
        filehandle.truncate()
    with open(misc_commands_py, "a") as filehandle:
        filehandle.write("None\n")

    print(f"{fg.YELLOW}Copying default config file to dist dir...{st.RESET_ALL}")
    copy(os.path.join("config.EXAMPLES.json"), os.path.join("dist", "config.json"))

    print(f"{fg.GREEN}Build success!{st.RESET_ALL} Executable can be found in /dist")

if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(fg.RED)
        print(f"{type(e)} : {e}")
        print(st.RESET_ALL)
        exit()
