import importlib
import os
from typing import Optional, Dict, Any

try:
    from .llm import LLMClient
except ImportError:
    from llm import LLMClient

class DynamicToolGenerator:
    def __init__(self, llm_client: LLMClient, tool_dir: str = "dynamic_tools"):
        self.llm_client = llm_client
        self.tool_dir = tool_dir
        os.makedirs(self.tool_dir, exist_ok=True)
        # Add the tool directory to the python path
        import sys
        if self.tool_dir not in sys.path:
            sys.path.append(self.tool_dir)

    async def generate_tool(self, tool_name: str, tool_description: str) -> Optional[Any]:
        """Generates and imports a new tool from a natural language description."""
        # Generate the python code for the tool
        tool_code = await self.llm_client.generate_tool_code(tool_name, tool_description)
        if not tool_code:
            return None

        # Save the tool to a file
        self._save_tool(tool_name, tool_code)

        # Import the tool
        return self._import_tool(tool_name)

    def _save_tool(self, tool_name: str, tool_code: str) -> None:
        """Saves the generated tool to a file."""
        file_path = os.path.join(self.tool_dir, f"{tool_name}.py")
        with open(file_path, "w") as f:
            f.write(tool_code)

    def _import_tool(self, tool_name: str) -> Optional[Any]:
        """Imports the generated tool."""
        try:
            module = importlib.import_module(tool_name)
            importlib.reload(module)
            return module
        except ImportError as e:
            print(f"Error importing tool {tool_name}: {e}")
            return None
