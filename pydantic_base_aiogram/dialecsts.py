from abc import ABC


class BaseDialects(ABC):
    INVALID_TYPE_DATA = 'invalid type of data'
    INVALID_FORMAT_DATE = 'invalid format of date'
    INPUT = 'Enter a valuef for `{field_name}`'
    CHOOSE_FROM_LIST = 'Choose value for `{field_name}`'
    CHOOSE_FROM_LIST_OR_INPUT = 'Choose or enter value for `{field_name}`'
    INPUT_STR = 'Enter a string for `{field_name}`'
    INPUT_STR_LIST = 'Enter a string items for `{field_name}`, separated by `{separator}`'
    INPUT_INT = 'Enter a number for `{field_name}`'
    INPUT_FLOAT = 'Enter a decimal number for `{field_name}`'
    CHOOSE = 'Select a value for `{field_name}`'
    CHOOSE_FROM_ENUM = 'Choose from options for `{field_name}`'
    CONTENT_TYPE_NOT_ALLOWED = 'Invalid content type, please select from the available options'
    CHOOSE_FROM_ENUM_OR_INPUT = 'Select or input a value for `{field_name}`'
    CHOOSE_FIELD_TYPE = 'Select type of `{field_name}`'
    BOOL_CHOICE_YES = 'Yes'
    BOOL_CHOICE_NO = 'No'
    BACK_BUTTON = 'Back'
    READY_BUTTON = 'Ready'
    SKIP_BUTTON = 'Skip'
    BACK_BUTTON_DATA = 'back'
    READY_BUTTON_DATA = 'ready'
    SKIP_STEP_DATA = 'skip_step'
    ADD_MORE = 'Add more?'
    SEND_FILE = 'Send a file for `{field_name}`'
    REQUIRED_ONLY_ONE_FILE = 'Please send only one file'
    SEND_FILES = 'Send files for `{field_name}`'


class EnDialects(BaseDialects):
    pass


class RuDialects(BaseDialects):
    INVALID_FORMAT_DATE = 'Неправилный формат даты. Должен совпадать с YYYY-MM-DD'
    INVALID_TYPE_DATA = 'Неправилный тип данных'
    INPUT = 'Введите значение для `{field_name}`'
    INPUT_STR = 'Введите строку для `{field_name}`'
    INPUT_STR_LIST = 'Введите строкы для `{field_name}`, разделенные `{separator}`'
    INPUT_INT = 'Введите число для `{field_name}`'
    INPUT_FLOAT = 'Введите десятичное число для `{field_name}`'
    CHOOSE = 'Выберите значение для `{field_name}`'
    CHOOSE_FROM_ENUM = 'Выберите из доступных вариантов для `{field_name}`'
    CONTENT_TYPE_NOT_ALLOWED = 'Недопустимый тип контента, выберите из доступных вариантов'
    CHOOSE_FROM_ENUM_OR_INPUT = 'Выберите или введите значение для `{field_name}`'
    BOOL_CHOICE_YES = 'Да'
    BOOL_CHOICE_NO = 'Нет'
    BACK_BUTTON = 'Назад'
    READY_BUTTON = 'Готово'
    SKIP_BUTTON = 'Пропустить'
    ADD_MORE = 'Добавить еще?'
    SEND_FILE = 'Отправить файл для `{field_name}`'
    SEND_FILES = 'Отправить файлы для `{field_name}`'
    REQUIRED_ONLY_ONE_FILE = 'Пожалуйста, отправьте только один файл'

