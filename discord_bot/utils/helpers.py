from datetime import datetime, timedelta
import pytz

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
        # self.logger = setup_logging()
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
        return self.isBotReady
