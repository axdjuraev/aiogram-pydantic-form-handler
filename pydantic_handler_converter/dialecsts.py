from abc import ABC


class BaseDialects(ABC):
    INPUT = 'input'
    INPUT_STR = 'input string'
    INPUT_INT = 'input number'
    INPUT_FLOAT = 'input number'
    CHOOSE = 'choose'
    CHOOSE_FROM_ENUM = CHOOSE
    BACK_BUTTON = 'back'
    SKIP_BUTTON = 'skip'
    SKIP_STEP_DATA = 'skip_step'


class EnDialects(BaseDialects):
    pass

