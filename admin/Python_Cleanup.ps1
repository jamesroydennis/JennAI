# Filename: Remove-PythonCaches.ps1 (Rewritten for JennAI/admin context)
# You will rename this to Project_Cleanup.ps1

<#
.SYNOPSIS
    Recursively deletes all Python-related cache folders within the JennAI project root.

.DESCRIPTION
    This script is specifically designed for the JennAI monorepo structure.
    It automatically determines the JennAI project's root directory (assumed to be
    one level up from its own location in 'JennAI/admin/').
    It then traverses all subdirectories under the JennAI root
    and removes any folders named '__pycache__', '.pytest_cache', and '.virtual_documents'.
    This is useful for ensuring Python reloads fresh code across all sub-projects
    and cleaning up editor-specific temporary files.

.EXAMPLE
    # Run from the JennAI/admin folder
    .\Remove-PythonCaches.ps1

.EXAMPLE
    # If added to PATH, or called from another script, it will always target JennAI root.
#>
param () # No parameters needed, path is calculated

# Calculate the JennAI project root based on the script's own location.
# Assumes this script is at 'C:\Users\jarde\Projects\JennAI\admin\Remove-PythonCaches.ps1'
# $PSScriptRoot is 'C:\Users\jarde\Projects\JennAI\admin'
# Going up one level: 'C:\Users\jarde\Projects\JennAI\'
$jennaiRootPath = (Split-Path -Path $PSScriptRoot -Parent)

# Define the cache folder names to be removed
$cacheFolders = @('__pycache__', '.pytest_cache', '.virtual_documents')

# Ensure the calculated path exists
if (-not (Test-Path $jennaiRootPath)) {
    Write-Error "Error: JennAI project root not found at calculated path '$jennaiRootPath'. Please check script location."
    exit 1
}

Write-Host "Starting comprehensive cleanup under JennAI root: $jennaiRootPath" -ForegroundColor Yellow

try {
    foreach ($folderName in $cacheFolders) {
        Write-Host "Searching for and deleting '$folderName' folders..." -ForegroundColor Yellow

        # Get-ChildItem finds all directories recursively under the root
        # and filters by the current cache folder name.
        Get-ChildItem -Path $jennaiRootPath -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.Name -eq $folderName) {
                Write-Host "  Deleting folder: $($_.FullName)" -ForegroundColor Red
                # -LiteralPath is important for paths that might contain [ ] or other special characters
                Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop
            }
        }
    }
    Write-Host "--------------------------------------------------------" -ForegroundColor Green
    Write-Host "Cleanup complete. All specified cache folders found within JennAI have been deleted." -ForegroundColor Green
}
catch {
    Write-Error "An error occurred during cleanup: $($_.Exception.Message)"
}
