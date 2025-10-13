"""
Test script to validate the generic server's JSON loading logic
"""
import json
from pathlib import Path

def test_tools_loading():
    """Test that the tools.json can be loaded correctly"""
    
    tools_file = Path("test_tools.json")
    
    if not tools_file.exists():
        print("❌ test_tools.json not found")
        return False
    
    try:
        with open(tools_file, 'r') as f:
            config = json.load(f)
        
        print("✅ Successfully loaded tools.json")
        
        # Validate structure
        required_fields = ["api_name", "base_url", "tools"]
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"✅ API Name: {config['api_name']}")
        print(f"✅ Base URL: {config['base_url']}")
        print(f"✅ Standard Tools: {len(config['tools'])}")
        print(f"✅ Composite Tools: {len(config.get('composite_tools', []))}")
        
        # Validate tools
        for idx, tool in enumerate(config['tools'], 1):
            required_tool_fields = ["name", "description", "input_schema", "endpoint_mapping"]
            for field in required_tool_fields:
                if field not in tool:
                    print(f"❌ Tool {idx} missing field: {field}")
                    return False
            print(f"  ✅ Tool {idx}: {tool['name']}")
        
        # Validate composite tools
        for idx, tool in enumerate(config.get('composite_tools', []), 1):
            required_composite_fields = ["name", "description", "input_schema", "endpoint_mappings", "orchestration_logic"]
            for field in required_composite_fields:
                if field not in tool:
                    print(f"❌ Composite Tool {idx} missing field: {field}")
                    return False
            print(f"  ✅ Composite Tool {idx}: {tool['name']} ({len(tool['endpoint_mappings'])} endpoints)")
        
        print("\n🎉 All validations passed!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_tools_loading()
