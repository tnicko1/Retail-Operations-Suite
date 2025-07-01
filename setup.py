import subprocess
import os
import sys

# The name of the configuration file for PyInstaller
SPEC_FILE = 'setup.spec'

def run_build():
    """Runs the PyInstaller build process."""
    # Check if the spec file exists
    if not os.path.exists(SPEC_FILE):
        print(f"Error: {SPEC_FILE} not found. Please ensure it's in the same directory.")
        sys.exit(1)

    # Run PyInstaller with the spec file
    print(f"--- Running PyInstaller with {SPEC_FILE} ---")
    try:
        # We use subprocess.run to execute the command
        subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--noconfirm', SPEC_FILE],
            check=True,
            text=True,
            capture_output=True # Capture output to check for errors
        )
        print("\n--- PyInstaller build complete. ---")
        print(f"--- The application is in the 'dist/Retail Operations Suite' folder. ---")
    except FileNotFoundError:
        print("\nError: Could not run PyInstaller.")
        print("Please make sure PyInstaller is installed (`pip install pyinstaller`).")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # If PyInstaller returns an error, print its output
        print("\n--- An error occurred during the build process. ---")
        print("--- PyInstaller Output: ---")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_build()
