# setup_windows.ps1
# Installs Scoop and eza if not present
if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    iex (irm get.scoop.sh)
}
scoop install eza