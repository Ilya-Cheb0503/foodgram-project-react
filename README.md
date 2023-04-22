# Foodrgam

Дипломная работа курса BackEnd Developer на языка Python
которая представляет из себя онлайн сервис с разработанным для него API.

С помощью данного сервиса пользователи имеют возможность делиться между собой
рецептами самых разных блюд, а также подписываться на интересных авторов
и помечать понравившиеся рецепты, добавляя в список "Избранное".

Кроме того, данный сервис позволяет наиболее удобным способом составить список
из продуктов, которые понадобятся для приготовления всех выбранных пользователем блюд
и скачать его перед походом в магазиг.

## О проекте 

- Проект был запущен на сервере: <http://158.160.99.229/> с помощью Docker контейнеров

Админ: oper


Пароль: oper050312
  
## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Зависимости
- Перечислены в файле backend/requirements.txt


## Для запуска на собственном сервере

1. Установите на сервере `docker` и `docker compose`
2. Создайте файл `/infra/.env` Шаблон для заполнения файла нахоится в `/infra/.env.example`
3. Из директории `/infra/` выполните команду `docker compose up -d --build`
5. Выполните миграции `docker compose exec -it app python manage.py migrate`
6. Создайте Администратора `docker compose exec -it app python manage.py createsuperuser`
7. Соберите статику `docker compose exec app python manage.py collectstatic --no-input`
8. Из директории `/backend/data` Загрузите ингредиенты
    
    `sudo docker exec -it backend python recipes/utils.py`
8. Документация к API находится по адресу: <http://158.160.99.229/api/docs/>.

## Автор

- [Илья Чебан](https://github.com/Ilya-Cheb0503)
