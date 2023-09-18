import os
import stat
import subprocess
import sys
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

def run_script(script_path: str, *script_args: str) -> None:
    try:
        # Ensure the bash script file has execute permissions
        st = os.stat(script_path)  # Get the current permissions of the file
        os.chmod(script_path, st.st_mode | stat.S_IEXEC)  # Add execute permission for the owner

        # Use subprocess.Popen for real-time output
        process = subprocess.Popen(
            [script_path] + list(script_args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Read from stdout and stderr in real-time
        for line in process.stdout:
            logger.info(line.strip())

        for line in process.stderr:
            logger.error(line.strip())

        # Wait for the process to complete and get the return code
        return_code = process.wait()

        if return_code != 0:
            logger.error(f"Script {script_path} failed with return code: {return_code}")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_path} failed with error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to execute script {script_path}: {str(e)}")
        sys.exit(1)

