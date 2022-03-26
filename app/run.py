# NOTICE
# This script is deprecated. Please use /app/run.sh instead.
# For migration reason, this script calls run.sh using subprocess.

import subprocess
from subprocess import PIPE

print("Notice: This script (/app/run.py) is deprecated.")
print("Please use /app/run.sh instead.")

shell_command = """
bash run.sh
"""

result = subprocess.run(shell_command, shell=True, stdout=PIPE, text=True)
print(result.stdout)
