from abc import ABC


class BaseDialects(ABC):
    INPUT = 'Enter a valuef for `{field_name}`'
    CHOOSE_FROM_LIST = 'Choose value for `{field_name}`'
    CHOOSE_FROM_LIST_OR_INPUT = 'Choose or enter value for `{field_name}`'
    INPUT_STR = 'Enter a string for `{field_name}`'
    INPUT_INT = 'Enter a number for `{field_name}`'
    INPUT_FLOAT = 'Enter a decimal number for `{field_name}`'
    CHOOSE = 'Select a value for `{field_name}`'
    CHOOSE_FROM_ENUM = 'Choose from options for `{field_name}`'
    CONTENT_TYPE_NOT_ALLOWED = 'Invalid content type, please select from the available options'
    CHOOSE_FROM_ENUM_OR_INPUT = 'Select or input a value for `{field_name}`'
    CHOOSE_FIELD_TYPE = 'Select type of `{field_name}`'
    BACK_BUTTON = 'Back'
    READY_BUTTON = 'Ready'
    SKIP_BUTTON = 'Skip'
    BACK_BUTTON_DATA = 'back'
    READY_BUTTON_DATA = 'ready'
    SKIP_STEP_DATA = 'skip_step'


class EnDialects(BaseDialects):
    pass


class RuDialects(BaseDialects):
    INPUT = 'Введите значение для `{field_name}`',
    INPUT_STR = 'Введите строку для `{field_name}`',
    INPUT_INT = 'Введите число для `{field_name}`',
    INPUT_FLOAT = 'Введите десятичное число для `{field_name}`',
    CHOOSE = 'Выберите значение для `{field_name}`',
    CHOOSE_FROM_ENUM = 'Выберите из доступных вариантов для `{field_name}`',
    CONTENT_TYPE_NOT_ALLOWED = 'Недопустимый тип контента, выберите из доступных вариантов',
    CHOOSE_FROM_ENUM_OR_INPUT = 'Выберите или введите значение для `{field_name}`',
    BACK_BUTTON = 'Назад',
    READY_BUTTON = 'Готово',
    SKIP_BUTTON = 'Пропустить',

