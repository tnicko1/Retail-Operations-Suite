# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import sys
from setuptools import setup, Command

# --- Application Information ---
APP_NAME = "Retail Operations Suite"
APP_VERSION = "2.1.0"
APP_DESCRIPTION = "A suite of tools for managing retail operations, including price tag generation."
COMPANY_NAME = "Nikoloz Taturashvili"

class BuildCommand(Command):
    description = "Build the application and create an installer."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Build the executable with PyInstaller
        pyinstaller_path = os.path.join(sys.prefix, 'Scripts', 'pyinstaller.exe')
        subprocess.run([pyinstaller_path, "main.spec", "--clean", "--noconfirm"], check=True)

        # Compile the installer with Inno Setup
        # Note: This assumes that the Inno Setup compiler (iscc.exe) is in your system's PATH.
        # You may need to provide the full path to iscc.exe.
        inno_setup_compiler = r"C:\Program Files (x86)\Inno Setup 6\iscc.exe"
        if not os.path.exists(inno_setup_compiler):
            print("Inno Setup compiler not found. Please install Inno Setup and ensure iscc.exe is in your PATH or update the path in setup.py.")
            sys.exit(1)
        subprocess.run([inno_setup_compiler, "setup.iss"], check=True)

setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=COMPANY_NAME,
    packages=[],
    cmdclass={
        'build': BuildCommand,
    }
)
