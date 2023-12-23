# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 20:50:32 2023

@author: dcask
"""
import os
import sys


# ----------------------set window's icon 
base_path = ''
try:
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")


VI_SERTIFICATE_VERIFY=False

VI_WINDOW_WIDTH=400
VI_WINDOW_HEIGHT=320
VI_WINDOW_ICON_PATH=os.path.join(base_path, 'images\\logo.png')
VI_WINDOW_NAME="viTools 1.02"

VI_TABPANEL_TAB1_NAME="API"
VI_TABPANEL_TAB2_NAME="Пользователи"
VI_TABPANEL_TAB3_NAME="Описание"
VI_TABPANEL_TAB4_NAME="Доступ к базам"
VI_TABPANEL_TAB5_NAME="Просмотры дашбордов"
VI_TABPANEL_TAB6_NAME="GitHub"
VI_TABPANEL_LOADER=os.path.join(base_path, "images\\loader.gif")
VI_TABPANEL_REFRESH="Перезагрузить"
VI_TABPANEL_ERROR_LINK="Ошибка связывания"

VI_EXPORT_PATH=os.path.join(base_path, 'dashboards\\')
VI_EXPORT_BUTTON_LABEL="Экспорт"
VI_IMPORT_BUTTON_LABEL="Импорт"
VI_USER_FIND_LABEL="Найти в "
VI_USER_LOAD='Загрузить XLS'
VI_USER_SAVE='Сохранить XLS'
VI_USER_SELECT='Выбрать всё'
VI_USER_DESELECT='Отменить выбор'
VI_USER_DEACTIVATE='Деактивировать выбранных'
VI_USER_DELETE='Удалить выбранных'
VI_USER_SAVEAS_LABEL="Сохранить как"
VI_USER_LOADAS_LABEL="Загрузить"
VI_USER_TOTAL_LABEL="Показано "
VI_USER_OF_LABEL=" из "

VI_LOGIN_TITLE="Подключиться к платформе"
VI_LOGIN_WINDOW_WIDTH=300
VI_LOGIN_WINDOW_HEIGHT=200
VI_LOGIN_URL_LABEL="URL"
VI_LOGIN_URL='http://'
VI_LOGIN_USER_LABEL='Пользователь:'
VI_LOGIN_USER='admin'
VI_LOGIN_PASSWORD_LABEL='Пароль:'
VI_LOGIN_BUTTON_LABEL='Войти'
VI_LOGIN_ERROR_FILL="Заполните необходимые поля"

VI_LICENSE_ADMIN_LABEL="Администраторов:"
VI_LICENSE_EDITOR_LABEL="Редакторов:"
VI_LICENSE_SF_LABEL="Операторов ввода:"
VI_LICENSE_OTHER_LABEL="Остальных:"
VI_LICENSE_TOTAL_LABEL='ВСЕГО:'
VI_LICENSE_LIMIT_LABEL=" из "

VI_ACCESS_BUTTON_LABEL='Связать'
VI_ACCESS_ROLES_LABEL='Связать роль:'

VI_API_TOKEN_LABEL="TOKEN"
VI_API_HEADERS_LABEL="Заголовки"
VI_API_BODY_LABEL="Тело запроса"
VI_API_OUTPUT_LABEL="Ответ"
VI_API_REFRESH_BUTTON="Обновить токен"
VI_API_EXPORT_BUTTON="Выгрузить"
VI_API_SEND_BUTTON="Отправить"
VI_API_SAVE_BUTTON="Сохранить"
VI_API_EMPTY="Пустой ответ"
VI_API_HEADER_ERROR="Некорректный json в заголовках\n"
VI_API_BODY_ERROR="Некорректный json в теле запроса\n"


VI_LOKI_KEY_LABEL="LOKI API KEY"
VI_LOKI_SINCE_LABEL="Часов в выборке"
VI_LOKI_SAVE="Сохранить в XLS"
VI_LOKI_REFRESH="Перезагрузить"
VI_LOKI_SAVEAS_LABEL="Сохранить как"