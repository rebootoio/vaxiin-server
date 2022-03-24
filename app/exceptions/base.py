class Error(Exception):
    pass


class ActionNotFound(Error):
    def __init__(self, name, message="Failed to find action by name"):
        self.name = name
        self.message = message


class ActionAlreadyExist(Error):
    def __init__(self, name, message="An action with the same name already exist"):
        self.name = name
        self.message = message


class ActionInUse(Error):
    def __init__(self, name, rules, message="The action is in use and cannot be deleted"):
        self.name = name
        self.rules = rules
        self.message = message


class RuleNameNotFound(Error):
    def __init__(self, name, message="Failed to find rule by name"):
        self.name = name
        self.message = message


class RuleAlreadyExist(Error):
    def __init__(self, name, message="A rule with the same name already exist"):
        self.name = name
        self.message = message


class StateNotFound(Error):
    def __init__(self, _id, message="Failed to find state by id"):
        self.id = _id
        self.message = message


class StateNotFoundForDevice(Error):
    def __init__(self, uid, message="Failed to find state by device uid"):
        self.uid = uid
        self.message = message


class WorkNotFound(Error):
    def __init__(self, _id, message="Failed to find work by id"):
        self.id = _id
        self.message = message


class WorkNotFoundForDevice(Error):
    def __init__(self, uid, message="Failed to find work by device uid"):
        self.uid = uid
        self.message = message


class DeviceNotFound(Error):
    def __init__(self, uid, message="Failed to find device by uid"):
        self.uid = uid
        self.message = message


class DeviceAlreadyExist(Error):
    def __init__(self, uid, message="A device with the same uid already exist"):
        self.uid = uid
        self.message = message


class WorkIsNotPending(Error):
    def __init__(self, _id, message="Work is not pending"):
        self.id = _id
        self.message = message


class WorkAlreadyExistForDevice(Error):
    def __init__(self, device_uid, message="Work for device already exist"):
        self.device_uid = device_uid
        self.message = message


class ManualWorkMustHaveRuleOrActions(Error):
    def __init__(self, message="Manual Work must supply either a rule or a list of actions"):
        self.message = message


class CredsNameNotFound(Error):
    def __init__(self, name, message="Creds not found by name"):
        self.name = name
        self.message = message


class CredsAlreadyExist(Error):
    def __init__(self, name, message="Creds already exist"):
        self.name = name
        self.message = message


class CredsAreSetAsDefault(Error):
    def __init__(self, name, message="Creds are set as default"):
        self.name = name
        self.message = message


class CredsInUse(Error):
    def __init__(self, name, devices, message="The creds are in use and cannot be deleted"):
        self.name = name
        self.devices = devices
        self.message = message


class DeviceInUse(Error):
    def __init__(self, uid, state_id, message="The creds are in use and cannot be deleted"):
        self.uid = uid
        self.state_id = state_id
        self.message = message


class RegexIsInvalid(Error):
    def __init__(self, regex_string, error, message="The regex provided does not compile"):
        self.regex_string = regex_string
        self.error = error
        self.message = message


class CredsNameIsReserved(Error):
    def __init__(self, name, message="The name provided for the credntials is reserved"):
        self.name = name
        self.message = message
