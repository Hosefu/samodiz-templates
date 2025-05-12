#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Начинаем очистку миграций...${NC}"

# Список приложений
APPS=(
    "apps/users"
    "apps/templates"
    "apps/generation"
    "apps/common"
)

# Очистка миграций
for app in "${APPS[@]}"; do
    echo -e "${YELLOW}Очистка миграций в ${app}...${NC}"
    
    # Проверяем существование директории
    if [ -d "$app/migrations" ]; then
        # Удаляем все файлы миграций, кроме __init__.py
        find "$app/migrations" -type f -not -name "__init__.py" -delete
        echo -e "${GREEN}✓ Миграции в ${app} очищены${NC}"
    else
        echo -e "${RED}✗ Директория ${app}/migrations не найдена${NC}"
    fi
done

echo -e "${YELLOW}Активация виртуального окружения...${NC}"
source new_venv/bin/activate

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Виртуальное окружение активировано${NC}"
else
    echo -e "${RED}✗ Ошибка активации виртуального окружения${NC}"
    exit 1
fi

echo -e "${YELLOW}Создание новых миграций...${NC}"
python3 manage.py makemigrations --skip-checks

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Новые миграции созданы${NC}"
else
    echo -e "${RED}✗ Ошибка создания миграций${NC}"
    exit 1
fi


echo -e "${GREEN}Готово! Все миграции пересозданы и применены.${NC}" 