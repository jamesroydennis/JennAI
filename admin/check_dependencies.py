import sys
import importlib
import subprocess
import shutil

def check_command(cmd, name):
    path = shutil.which(cmd)
    if path:
        print(f"{name}: ✅ ({path})")
    else:
        print(f"{name}: ❌ NOT FOUND")

def check_python_package(pkg):
    try:
        importlib.import_module(pkg)
        print(f"Python package '{pkg}': ✅")
    except ImportError:
        print(f"Python package '{pkg}': ❌ NOT INSTALLED")

def main():
    print("=== System Dependency Checks ===")
    check_command("nvm", "nvm")
    check_command("node", "Node.js")
    check_command("npm", "npm")
    check_command("sass", "Sass CLI")
    check_command("eza", "eza (tree view)")
    check_command("allure", "Allure CLI")
    check_command("java", "Java")

    print("\n=== Python Package Checks ===")
    python_packages = [
        "flask", "flask_cors", "flask_assets", "inquirerpy",
        "numpy", "pandas", "requests", "matplotlib", "jupyter", "markdown"
    ]
    for pkg in python_packages:
        check_python_package(pkg)

if __name__ == "__main__":
    main()