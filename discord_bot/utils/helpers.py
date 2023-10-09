from datetime import datetime

class DateTimeManager:
    def __init__(self):
        # self.logger = setup_logging()
        self.format_string = "%Y-%m-%d %H:%M:%S"

    def get_current_datetime(self):
        """
        Get the current date/time as a formatted string.
        """
        dt = datetime.now()
        return dt.strftime(self.format_string)
    
    def parse_datetime(self, date_string):
        """
        Parses a date and time string into a datetime object.
        """
        return datetime.strptime(date_string, self.format_string)
    
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
