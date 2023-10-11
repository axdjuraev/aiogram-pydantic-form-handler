from abc import ABC


class BaseDialects(ABC):
    INPUT = 'Enter a valuef for `{field_name}`'
    INPUT_STR = 'Enter a string for `{field_name}`'
    INPUT_INT = 'Enter a number for `{field_name}`'
    INPUT_FLOAT = 'Enter a decimal number for `{field_name}`'
    CHOOSE = 'Select a value for `{field_name}`'
    CHOOSE_FROM_ENUM = 'Choose from options for `{field_name}`'
    CONTENT_TYPE_NOT_ALLOWED = 'Invalid content type, please select from the available options'
    CHOOSE_FROM_ENUM_OR_INPUT = 'Select or input a value for `{field_name}`'
    BACK_BUTTON = 'Back'
    READY_BUTTON = 'Ready'
    READY_BUTTON_DATA = 'ready'
    SKIP_BUTTON = 'Skip'
    SKIP_STEP_DATA = 'skip_step'


class EnDialects(BaseDialects):
    pass

