from pathlib import Path
from ..models.schemas import ToolModel
import json
import shutil

class ServerGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"

    def generate_server(self, tool_model: ToolModel, server_name: str, output_dir: str) -> str:
        """Generate a complete MCP server from tool model using declarative JSON approach"""

        output_path = Path(output_dir) / server_name
        output_path.mkdir(parents=True, exist_ok=True)

        # Copy the entire MCP server template structure
        mcp_server_template = self.template_dir / "mcp_server"
        if mcp_server_template.exists():
            # Copy the entire template directory structure
            self._copy_template_structure(mcp_server_template, output_path)

        # Save tools.json
        tools_data = tool_model.model_dump()
        with open(output_path / "tools.json", 'w') as f:
            json.dump(tools_data, f, indent=2)

        # Generate README from template
        readme = self._generate_readme(tool_model, server_name, str(output_path))
        (output_path / "README.md").write_text(readme)

        # Generate pyproject.toml from template
        pyproject = self._generate_pyproject(server_name, tool_model.api_name)
        (output_path / "pyproject.toml").write_text(pyproject)

        # Generate .env.example from template
        env_example = self._generate_env_example(tool_model.api_name)
        (output_path / ".env.example").write_text(env_example)

        return str(output_path)

    def _copy_template_structure(self, template_dir: Path, output_dir: Path):
        """Copy the entire template directory structure to the output directory"""
        for item in template_dir.rglob("*"):
            if item.is_file():
                # Calculate relative path from template_dir
                relative_path = item.relative_to(template_dir)
                target_path = output_dir / relative_path
                
                # Create parent directories if they don't exist
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(item, target_path)

    def _generate_readme(self, tool_model: ToolModel, server_name: str, server_path: str) -> str:
        """Generate README from template"""
        
        # Build tools list
        tools_list = ""
        if tool_model.tools:
            for tool in tool_model.tools:
                desc = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                tools_list += f"- **`{tool.name}`**: {desc}\n"
        else:
            tools_list = "No standard tools defined.\n"
        
        # Build composite tools section
        composite_tools_section = ""
        if tool_model.composite_tools:
            composite_tools_section = "### Composite Tools (Multi-Endpoint Orchestrations)\n\n"
            for tool in tool_model.composite_tools:
                desc = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                endpoint_count = len(tool.endpoint_mappings)
                composite_tools_section += f"- **`{tool.name}`**: {desc} *(combines {endpoint_count} endpoints)*\n"
        
        # Read template
        template_path = self.template_dir / "README.template.md"
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace placeholders
        readme = template_content.replace("{server_name}", server_name)
        readme = readme.replace("{api_name}", tool_model.api_name)
        readme = readme.replace("{tools_list}", tools_list)
        readme = readme.replace("{composite_tools_section}", composite_tools_section)
        readme = readme.replace("{server_path}", server_path)
        
        return readme

    def _generate_pyproject(self, server_name: str, api_name: str) -> str:
        """Generate pyproject.toml from template"""
        
        template_path = self.template_dir / "pyproject.template.toml"
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        pyproject = template_content.replace("{server_name}", server_name)
        pyproject = pyproject.replace("{api_name}", api_name)
        
        return pyproject

    def _generate_env_example(self, api_name: str) -> str:
        """Generate .env.example from template"""
        
        template_path = self.template_dir / ".env.template"
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        env_example = template_content.replace("{api_name}", api_name)
        
        return env_example
