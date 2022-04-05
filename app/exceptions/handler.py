class Error(Exception):
    pass


class ActionError(Error):
    def __init__(self, error, message="Failed to run action"):
        self.error = error
        self.message = message


class KeystrokeError(ActionError):
    def __init__(self, error, message="Failed to run keystroke"):
        self.error = error
        self.message = message


class SleepError(ActionError):
    def __init__(self, error, message="Failed to sleep"):
        self.error = error
        self.message = message


class GetScreenshotError(ActionError):
    def __init__(self, error, message="Failed to get screenshot"):
        self.error = error
        self.message = message


class SendScreenshotError(ActionError):
    def __init__(self, error, message="Failed to send screenshot"):
        self.error = error
        self.message = message


class IpmitoolError(ActionError):
    def __init__(self, error, message="Failed to run ipmitool"):
        self.error = error
        self.message = message


class HttpRequestError(ActionError):
    def __init__(self, error, message="Failed to do a GET request"):
        self.error = error
        self.message = message


class ConsoleError(Error):
    def __init__(self, error, message="Failed to open console"):
        self.error = error
        self.message = message


class ModelNotSupportedError(ConsoleError):
    def __init__(self, error, message="Failed to find open console method for model"):
        self.error = error
        self.message = message


class OpenConsoleError(ConsoleError):
    def __init__(self, error, message="Failed to find open console"):
        self.error = error
        self.message = message
