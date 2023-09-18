import os
import subprocess
from .logger import setup_logging

# Setting up logging
logger = setup_logging()

class GitUtil:
    def __init__(self, ssh_key_path):
        self.ssh_key_path = ssh_key_path
        self.git_ssh_command = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"
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
            subprocess.check_call(['git', 'clone', '-b', branch, repo_url, target_directory])
            logger.info(f"Repository '{repo_url}' cloned successfully into '{target_directory}'.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone the repository: '{repo_url}'. Error: {e}")
            raise

    def checkout(self, directory, branch):
        """
        Checkout to a specific branch in a Git directory.

        :param directory: Directory of the git repo.
        :param branch: The branch to checkout to.
        :return: None
        """
        try:
            subprocess.check_call(['git', '-C', directory, 'checkout', branch])
            logger.info(f"Checked out to '{branch}' in '{directory}'.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to checkout to branch: '{branch}'. Error: {e}")
            raise
        
    @staticmethod
    def get_git_branch(self):
        """
        Get the active Git branch.

        :return: Name of the current branch.
        """
        try:
            branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
            return branch
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get the active Git branch. Error: {e}")
            raise