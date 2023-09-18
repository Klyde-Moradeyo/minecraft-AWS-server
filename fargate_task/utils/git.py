import os
import subprocess
from git import Repo
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

class GitUtil:
    def __init__(self, ssh_key_path):
        self.ssh_key_path = ssh_key_path
        self.git_ssh_command = f"ssh -i {ssh_key_path} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
        os.environ['GIT_SSH_COMMAND'] = self.git_ssh_command

    def clone(self, repo_url, target_directory, branch='main'):
        """
        Clone a Git repository.

        :param repo_url: URL of the git repository.
        :param target_directory: Directory where the repo should be cloned.
        :param branch: The branch to clone. Default is 'main'.
        :return: None
        """
        try:
            repo = Repo.clone_from(repo_url, target_directory, branch)
        except Exception as e:
            raise Exception(f"Git clone failed:\n{str(e)}")
        
        return repo
    
    # Should use git python
    # def checkout(self, directory, branch):
    #     """
    #     Checkout to a specific branch in a Git directory.

    #     :param directory: Directory of the git repo.
    #     :param branch: The branch to checkout to.
    #     :return: None
    #     """
    #     try:
    #         subprocess.check_call(['git', '-C', directory, 'checkout', branch])
    #         logger.info(f"Checked out to '{branch}' in '{directory}'.")
    #     except subprocess.CalledProcessError as e:
    #         logger.error(f"Failed to checkout to branch: '{branch}'. Error: {e}")
    #         raise
        
    @staticmethod
    def get_git_branch() -> str:
        """
        Get the Environment's Git Branch

        :return: Name of the Environment's branch.
        """
        dev_env = "DEV"
        prod_env = "PROD"
        current_env = os.environ.get('ENVIRONMENT')

        if current_env is None:
            raise ValueError("ENVIRONMENT variable is not set.")
        
        current_env = current_env.upper()
        
        if current_env == dev_env:
            return 'dev'
        elif current_env == prod_env:
            return 'main'
        else:
            raise ValueError(f"Unsupported ENVIRONMENT value: {current_env}. Supported values are '{dev_env}' and '{prod_env}'.")
