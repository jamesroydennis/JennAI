import subprocess

def main():
    print("\nTo set JAVA_HOME and update your PATH for Allure CLI, run the following in PowerShell:")
    print()
    print('$env:JAVA_HOME = (scoop prefix openjdk)')
    print('$env:PATH = "$env:JAVA_HOME\\bin;$env:PATH"')
    print()
    print("Or, to make these changes permanent, add JAVA_HOME as a user environment variable with value:")
    print("    C:\\Users\\jarde\\scoop\\apps\\openjdk\\current")
    print("and add %JAVA_HOME%\\bin to your user PATH.")

    # Optionally, check if Java is available
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("\nJava is available:")
            print(result.stderr or result.stdout)
        else:
            print("\nJava is NOT available in your PATH.")
    except Exception:
        print("\nJava is NOT available in your PATH.")

if __name__ == "__main__":
    main()