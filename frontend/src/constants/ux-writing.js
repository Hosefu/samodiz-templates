// frontend/src/constants/ux-writing.js

export const APP_TITLE = "Генератор документов";

// Navigation
export const NAV_HOME = "Главная";
export const NAV_ADMIN = "Админ-панель";
export const NAV_LOGIN = "Вход";
export const NAV_LOGOUT = "Выход";
export const NAV_GREETING = (username) => `Привет, ${username}!`;

// Diagnostics
export const DIAG_TITLE = "Диагностика";
export const DIAG_CURRENT_PATH = "Текущий путь:";
export const DIAG_AUTH_STATUS = "Аутентификация:";
export const DIAG_AUTH_YES = "Да";
export const DIAG_AUTH_NO = "Нет";
export const DIAG_API_STATUS = "API статус:";
export const DIAG_API_CHECKING = "Проверка...";
export const DIAG_API_AVAILABLE = "API доступен";
export const DIAG_API_UNAVAILABLE = (status, statusText) => `API недоступен: ${status} ${statusText}`;
export const DIAG_API_ERROR = (message) => `Ошибка подключения к API: ${message}`;
export const DIAG_ERROR_PREFIX = "Ошибка:";
export const DIAG_USER_INFO = (username, role) => `Пользователь: ${username} (${role})`;
export const DIAG_USER_ROLE_ADMIN = "администратор";
export const DIAG_USER_ROLE_USER = "пользователь";

// Home Page (Template Selection/Generation)
export const HOME_SELECT_TEMPLATE_TITLE = "Выберите шаблон документа";
export const HOME_LOADING_TEMPLATES = "Загрузка шаблонов...";
export const HOME_NO_TEMPLATES_FOUND = "Шаблоны не найдены.";
export const HOME_FETCH_TEMPLATES_ERROR = "Не удалось загрузить шаблоны. Попробуйте позже.";
export const HOME_TEMPLATE_VERSION = "Версия:";
export const HOME_TEMPLATE_PAGES_COUNT = (count) => `${count} стр.`;
export const HOME_TEMPLATE_NO_PAGES = "0 стр.";
export const HOME_INVALID_TEMPLATE_STRUCTURE = "Ошибка структуры шаблона. Пожалуйста,";
export const HOME_SELECT_OTHER_TEMPLATE_LINK = "выберите другой шаблон";
export const HOME_FILL_DATA_TITLE = (templateName) => `Заполните данные для "${templateName}"`;
export const HOME_BACK_TO_SELECTION_BUTTON = "Назад к выбору";
export const HOME_NO_FIELDS_IN_TEMPLATE = "В этом шаблоне нет полей для заполнения.";
export const HOME_GENERATE_BUTTON = "Сгенерировать документ";
export const HOME_GENERATING_BUTTON = "Генерация...";
export const HOME_GENERATION_ERROR_MESSAGE = "Ошибка генерации документа. Проверьте данные и попробуйте снова.";
export const HOME_GENERATION_SUCCESS_TITLE = "Документ успешно сгенерирован";
export const HOME_CREATE_NEW_BUTTON = "Создать новый";
export const HOME_PREVIEW_TITLE = "Предпросмотр документа";
export const HOME_PREVIEW_UNAVAILABLE = "Предпросмотр недоступен.";
export const HOME_DOWNLOAD_BUTTON = "Скачать документ";
export const HOME_CREATE_ANOTHER_BUTTON = "Создать еще один";

// Login Page
export const LOGIN_PAGE_TITLE = "Вход в систему";
export const LOGIN_USERNAME_LABEL = "Имя пользователя:";
export const LOGIN_PASSWORD_LABEL = "Пароль:";
export const LOGIN_SUBMIT_BUTTON = "Войти";
export const LOGIN_ERROR_MESSAGE = "Ошибка входа. Проверьте имя пользователя и пароль.";

// Admin Layout
export const ADMIN_SIDEBAR_TITLE = "Панель администратора";
export const ADMIN_SIDEBAR_DASHBOARD = "Обзор";
export const ADMIN_SIDEBAR_TEMPLATES = "Шаблоны";
export const ADMIN_SIDEBAR_BACK_TO_PUBLIC = "Вернуться на сайт";
export const ADMIN_HEADER_DASHBOARD = "Обзор";
export const ADMIN_HEADER_TEMPLATES = "Шаблоны";
export const ADMIN_HEADER_CREATE = "Создать";
export const ADMIN_HEADER_EDIT = "Редактировать";

// Admin Dashboard
export const ADMIN_DASHBOARD_TITLE = "Панель управления генератором документов";
export const ADMIN_DASHBOARD_WELCOME = "Добро пожаловать в панель администратора. Здесь вы можете управлять шаблонами и генерировать документы.";
export const ADMIN_DASHBOARD_TEMPLATES_CARD_TITLE = "Шаблоны";
export const ADMIN_DASHBOARD_TEMPLATES_CARD_INFO = (count) => `У вас ${count} шаблонов в системе.`;
export const ADMIN_DASHBOARD_MANAGE_TEMPLATES_BUTTON = "Управление шаблонами";
export const ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_TITLE = "Создать новый шаблон";
export const ADMIN_DASHBOARD_CREATE_TEMPLATE_CARD_INFO = "Начните с создания нового шаблона для ваших документов.";
export const ADMIN_DASHBOARD_CREATE_TEMPLATE_BUTTON = "Создать шаблон";

// Admin Template List
export const ADMIN_TEMPLATE_LIST_TITLE = "Управление шаблонами";
export const ADMIN_TEMPLATE_LIST_CREATE_BUTTON = "Создать новый шаблон";
export const ADMIN_TEMPLATE_LIST_LOADING = "Загрузка шаблонов...";
export const ADMIN_TEMPLATE_LIST_ERROR = (error) => `Ошибка загрузки шаблонов: ${error}`;
export const ADMIN_TEMPLATE_LIST_NO_TEMPLATES = "Шаблоны еще не созданы.";
export const ADMIN_TEMPLATE_LIST_TABLE_HEADER_NAME = "Название";
export const ADMIN_TEMPLATE_LIST_TABLE_HEADER_VERSION = "Версия";
export const ADMIN_TEMPLATE_LIST_TABLE_HEADER_TYPE = "Тип";
export const ADMIN_TEMPLATE_LIST_TABLE_HEADER_PAGES = "Страниц";
export const ADMIN_TEMPLATE_LIST_TABLE_HEADER_ACTIONS = "Действия";
export const ADMIN_TEMPLATE_LIST_EDIT_BUTTON = "Редактировать";
export const ADMIN_TEMPLATE_LIST_DELETE_BUTTON = "Удалить";
export const ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_TITLE = "Подтвердите удаление";
export const ADMIN_TEMPLATE_LIST_CONFIRM_DELETE_MSG = (name) => `Вы уверены, что хотите удалить шаблон "${name}"? Это действие необратимо.`;
export const ADMIN_TEMPLATE_LIST_CANCEL_BUTTON = "Отмена";

// Template Create
export const TEMPLATE_CREATE_TITLE = "Создание нового шаблона";
export const TEMPLATE_CREATE_DESCRIPTION = "Введите основную информацию для вашего шаблона.";
export const TEMPLATE_CREATE_NAME_LABEL = "Название шаблона";
export const TEMPLATE_CREATE_NAME_PLACEHOLDER = "Например, Счет-фактура";
export const TEMPLATE_CREATE_VERSION_LABEL = "Версия";
export const TEMPLATE_CREATE_VERSION_PLACEHOLDER = "1.0";
export const TEMPLATE_CREATE_TYPE_LABEL = "Тип выходного файла";
export const TEMPLATE_CREATE_SELECT_TYPE = "Выберите тип файла";
export const TEMPLATE_CREATE_ERROR = (msg) => `Не удалось создать шаблон: ${msg}`;
export const TEMPLATE_CREATE_SUBMIT_BUTTON = "Создать и перейти к страницам";
export const TEMPLATE_CREATE_SUBMITTING_BUTTON = "Создание...";

// Общие
export const REQUIRED_FIELD_MARKER = "*";
export const LOADING_TEXT = "Загрузка...";
export const REQUIRED_ERROR_MSG = (fieldName) => `${fieldName} обязательно для заполнения.`;
export const UNKNOWN_ERROR_MSG = "Произошла неизвестная ошибка";
export const API_AVAILABLE_MSG = "API доступен";
export const BACK_TO_LIST_BUTTON = "Вернуться к списку";
export const TEMPLATE_NAME_DEFAULT = "Безымянный шаблон";
export const PAGE_NAME_DEFAULT = "Безымянная страница";
export const ASSET_NAME_DEFAULT = "Безымянный ассет";
export const COPY_PATH_FAILED_MSG = "Не удалось скопировать путь";
export const UPLOAD_FILE_FAILED_MSG = "Ошибка загрузки файла";

// Кнопки действий
export const CREATE_BUTTON = "Создать";
export const EDIT_BUTTON = "Редактировать";
export const SAVE_BUTTON = "Сохранить";
export const CANCEL_BUTTON = "Отмена";
export const DELETE_BUTTON = "Удалить";
export const SAVING_BUTTON_SUFFIX = "...";
export const CREATING_BUTTON_SUFFIX = "...";
export const DELETING_BUTTON_SUFFIX = "...";

// Конкретные страницы
export const PAGE_CREATE_FIELD_DEFAULT_TITLE = "Заголовок документа";
export const PAGE_CREATE_FIELD_DEFAULT_NAME = "Имя получателя"; 