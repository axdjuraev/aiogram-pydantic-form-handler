from abc import ABC


class BaseDialects(ABC):
    INPUT = 'input'
    INPUT_STR = 'input string for `{field_name}`'
    INPUT_INT = 'input number for `{field_name}`'
    INPUT_FLOAT = 'input number for `{field_name}`'
    CHOOSE = 'choose value of `{field_name}`'
    CHOOSE_FROM_ENUM = 'choose value of `{field_name}`'
    CHOOSE_FROM_ENUM_OR_INPUT = 'choose or input value of `{field_name}`'
    BACK_BUTTON = 'back'
    SKIP_BUTTON = 'skip'
    SKIP_STEP_DATA = 'skip_step'


class EnDialects(BaseDialects):
    pass

