
import pytz
import requests
from datetime import datetime, timedelta
from .logger import setup_logging

class DateTimeManager:
    def __init__(self):
        # self.logger = setup_logging()
        self.format_string = "%Y-%m-%d %H:%M:%S"

    def get_current_datetime(self):
        """
        Get the current date/time as a formatted string.
        """
        dt = datetime.now(pytz.utc)
        return dt.strftime(self.format_string)
    
    def parse_datetime(self, date_string):
        """
        Parses a date and time string into a datetime object.
        """
        return datetime.strptime(date_string, self.format_string)
    
    def get_time_delta(self, seconds=0, minutes=0, hours=0, days=0):
        """
        Returns a timedelta object representing the specified time delta.
        """
        return timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)

class BotReady:
    def __init__(self):
        self.logger = setup_logging()
        self.isBotReady = False

    def get_status(self):
        """
        Get Discord Bot Status
        """
        return self.isBotReady
    
    def set_status(self, value: bool):
        """
        Get Discord Bot Status
        """
        self.isBotReady = value
        self.logger.info(f"Setting Discord Bot to: '{value}'")
        return self.isBotReady

###################################

def get_versions(envs, logger):
    """
    Get Versions of the minecraft infrastructure
    """ 
    logger.info("Getting Software Versions...")
    repo = envs["GITHUB_REPO"]
    token = envs["GITHUB_TOKEN"]

    PREFIXES = ["MSMC_", "SMB_", "MSIH_" , "MCI_"]
    HEADERS = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }

    def get_all_commits_from_main():
        commits = []
        page = 1

        while True:
            url = f"https://api.github.com/repos/{repo}/commits?sha=main&page={page}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            page_data = response.json()
            if not page_data:
                break

            commits.extend(page_data)
            page += 1

        return {commit['sha'] for commit in commits}

    def get_all_tags():
        tags = []
        page = 1

        while True:
            url = f"https://api.github.com/repos/{repo}/tags?page={page}"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            page_data = response.json()
            if not page_data:
                break

            tags.extend(page_data)
            page += 1

        return tags

    def get_latest_tag_for_prefix(tags, prefix):
        prefixed_tags = [tag for tag in tags if tag['name'].startswith(prefix)]
        return prefixed_tags[0]['name'] if prefixed_tags else None

    # Filter out tags that aren't part of the main branch
    commit_shas_main = get_all_commits_from_main()
    tags = [tag for tag in get_all_tags() if tag['commit']['sha'] in commit_shas_main]

    # Find latest tag for each prefix
    latest_tags = {}
    for prefix in PREFIXES:
        latest_tags[prefix] = get_latest_tag_for_prefix(tags, prefix).replace(prefix, "")

    SMB_discord_bot = latest_tags["SMB_"]
    MSMC_fargate = latest_tags["MSMC_"]
    MCI_lambda = latest_tags["MCI_"]
    MSIH_infra_handler = latest_tags["MSIH_"]
    
    logger.info(f"Versions - {latest_tags}")

    return SMB_discord_bot, MSMC_fargate, MCI_lambda, MSIH_infra_handler