import json
from pathlib import Path

notebook_path = Path(r"c:\Users\shaur\Desktop\Learnings\linkedin_automation\tests\01_linkedin_connection.ipynb")

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The cell we want to modify is the second one (index 1)
# It contains:
# "from pathlib import Path\n",
# "import sys, os\n",
# "utils_path = Path(\"C:/Users/shaur/Desktop/Learnings/linkedin_automation/src\")\n",
# "prompts_path = Path(\"C:/Users/shaur/Desktop/Learnings/linkedin_automation/prompts\")\n",
# "sys.path.append(str(utils_path))\n",
# "sys.path.append(str(prompts_path))"

target_source = [
    "from pathlib import Path\n",
    "import sys, os\n",
    "project_root = Path(\"C:/Users/shaur/Desktop/Learnings/linkedin_automation\")\n",
    "utils_path = project_root / \"src\"\n",
    "prompts_path = project_root / \"prompts\"\n",
    "sys.path.append(str(project_root))\n",
    "sys.path.append(str(utils_path))\n",
    "sys.path.append(str(prompts_path))"
]

nb['cells'][1]['source'] = target_source

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated successfully.")
