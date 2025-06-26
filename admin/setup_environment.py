#!/usr/bin/env python
import subprocess
import sys
from InquirerPy import inquirer

ENV_NAME = "jennai-root"
ENV_YAML = "environment.yaml"
SCOOP_TOOLS = [
    ("java", "scoop bucket add java"),
    ("openjdk", "scoop install openjdk"),
    ("allure", "scoop install allure"),
    ("eza", "scoop install eza"),
]

def run_cmd(cmd, shell=True):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, shell=shell)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
    return result.returncode

def deactivate_env():
    print("Deactivating conda environment...")
    run_cmd("conda deactivate")

def reinstall_env():
    print(f"Removing and recreating environment '{ENV_NAME}'...")
    run_cmd(f"conda env remove -n {ENV_NAME} -y")
    run_cmd(f"conda env create -f {ENV_YAML}")

def update_env():
    print(f"Updating environment '{ENV_NAME}'...")
    run_cmd(f"conda env update --file {ENV_YAML} --prune")

def install_scoop_tools():
    print("Installing system tools with Scoop...")
    for name, cmd in SCOOP_TOOLS:
        print(f"\nInstalling {name}...")
        run_cmd(cmd)

def main():
    while True:
        choice = inquirer.select(
            message="JennAI Environment Manager - Choose an action:",
            choices=[
                "Deactivate environment",
                "Reinstall environment",
                "Update environment",
                "Install Scoop system tools",
                "Exit"
            ]
        ).execute()
        if choice == "Deactivate environment":
            deactivate_env()
        elif choice == "Reinstall environment":
            reinstall_env()
        elif choice == "Update environment":
            update_env()
        elif choice == "Install Scoop system tools":
            install_scoop_tools()
        else:
            print("Goodbye!")
            sys.exit(0)
        # Print instructions for setting JAVA_HOME, etc.
    # (as in previous examples)

    # Optionally, prompt the user before launching the admin console
    input("\nPress Enter to launch the JennAI Admin Console...")

    # Launch admin/42.py using the same Python interpreter
    admin_console = Path(__file__).parent / "42.py"
    subprocess.run([sys.executable, str(admin_console)])

if __name__ == "__main__":
    main()