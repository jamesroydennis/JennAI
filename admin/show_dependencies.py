#!/usr/bin/env python
"""
Shows the project dependencies from environment.yaml in a structured format.
This provides insight into conda dependencies, pip requirements, and external tools.
"""
import sys
from pathlib import Path
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# --- Root Project Path Setup ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def show_dependencies(console=None):
    """
    Displays project dependencies from environment.yaml in a structured format.
    """
    if console is None:
        console = Console()
    
    environment_file = ROOT / "environment.yaml"
    
    if not environment_file.exists():
        console.print(f"[red]Error: environment.yaml not found at {environment_file}[/red]")
        return
    
    try:
        with open(environment_file, 'r', encoding='utf-8') as f:
            env_data = yaml.safe_load(f)
        
        # Display environment name and channels
        console.print(Panel.fit(
            f"[bold cyan]Environment:[/bold cyan] {env_data.get('name', 'N/A')}\n"
            f"[bold cyan]Channels:[/bold cyan] {', '.join(env_data.get('channels', []))}",
            title="[bold]Conda Environment Info[/bold]",
            border_style="cyan"
        ))
        console.print()
        
        # Parse dependencies
        dependencies = env_data.get('dependencies', [])
        conda_deps = []
        pip_deps = []
        
        for dep in dependencies:
            if isinstance(dep, str):
                conda_deps.append(dep)
            elif isinstance(dep, dict) and 'pip' in dep:
                pip_deps.extend(dep['pip'])
        
        # Create conda dependencies table
        if conda_deps:
            conda_table = Table(title="[bold]Conda Dependencies[/bold]", show_header=True, header_style="bold magenta")
            conda_table.add_column("Package", style="cyan", no_wrap=True)
            conda_table.add_column("Version/Channel", style="green")
            
            for dep in conda_deps:
                if '::' in dep:
                    # Channel-specific dependency
                    channel, package = dep.split('::', 1)
                    conda_table.add_row(package, f"from {channel}")
                elif '=' in dep:
                    # Versioned dependency
                    parts = dep.split('=')
                    package = parts[0]
                    version = '='.join(parts[1:])
                    conda_table.add_row(package, version)
                else:
                    # Simple dependency
                    conda_table.add_row(dep, "latest")
            
            console.print(conda_table)
            console.print()
        
        # Create pip dependencies table
        if pip_deps:
            pip_table = Table(title="[bold]Pip Dependencies[/bold]", show_header=True, header_style="bold blue")
            pip_table.add_column("Package/Source", style="cyan")
            pip_table.add_column("Type", style="yellow")
            
            for dep in pip_deps:
                if dep.startswith('-r '):
                    # Requirements file reference
                    req_file = dep[3:]
                    pip_table.add_row(req_file, "requirements file")
                elif dep.startswith('-e '):
                    # Editable install
                    pip_table.add_row(dep[3:], "editable")
                elif dep.startswith('git+'):
                    # Git repository
                    pip_table.add_row(dep, "git repository")
                else:
                    # Regular pip package
                    pip_table.add_row(dep, "pip package")
            
            console.print(pip_table)
            console.print()
        
        # Read external tools section from the file (comments at the top)
        with open(environment_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract external tools section
        if "EXTERNAL TOOLS" in content and "dependencies:" in content:
            external_section = content.split("dependencies:")[0]
            if "EXTERNAL TOOLS" in external_section:
                # Parse external tools from comments
                external_tools = []
                lines = external_section.split('\n')
                current_tool = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('# - ') and ':' in line:
                        # New tool definition
                        tool_name = line.split('# - ')[1].split(':')[0].strip()
                        description = line.split(':', 1)[1].strip() if ':' in line else ""
                        current_tool = {"name": tool_name, "description": description, "commands": []}
                        external_tools.append(current_tool)
                    elif line.startswith('#     ') and current_tool:
                        # Command or additional info for current tool
                        command = line.replace('#     ', '').strip()
                        if command and not command.startswith('# '):
                            current_tool["commands"].append(command)
                
                if external_tools:
                    external_table = Table(title="[bold]External Tools (Manual Installation)[/bold]", 
                                         show_header=True, header_style="bold red")
                    external_table.add_column("Tool", style="red", no_wrap=True)
                    external_table.add_column("Description", style="yellow")
                    external_table.add_column("Sample Command", style="green")
                    
                    for tool in external_tools:
                        sample_cmd = tool["commands"][0] if tool["commands"] else "See documentation"
                        external_table.add_row(
                            tool["name"], 
                            tool["description"], 
                            sample_cmd
                        )
                    
                    console.print(external_table)
                    console.print()
        
        # Summary
        total_conda = len(conda_deps)
        total_pip = len(pip_deps)
        console.print(Panel.fit(
            f"[bold green]Total Dependencies:[/bold green]\n"
            f"• Conda packages: {total_conda}\n"
            f"• Pip packages/sources: {total_pip}\n"
            f"• External tools: Manual installation required",
            title="[bold]Summary[/bold]",
            border_style="green"
        ))
        
    except yaml.YAMLError as e:
        console.print(f"[red]Error parsing environment.yaml: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error reading environment.yaml: {e}[/red]")

def main():
    """Main entry point for standalone execution."""
    console = Console()
    show_dependencies(console)

if __name__ == "__main__":
    main()
