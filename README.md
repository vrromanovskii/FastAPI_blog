# FastAPI_blog

# Marketplace Blog API

Бэкенд для блог-платформы с аутентификацией, управлением публикациями, мягким удалением и пагинацией.  
Проект написан на **FastAPI** с использованием **PostgreSQL** (в Docker), **SQLAlchemy**, **Alembic**, **JWT** и отправкой email при регистрации.


- Регистрация и аутентификация пользователей (JWT токены)
- CRUD операции с публикациями:
  - Создание (только авторизованные)
  - Просмотр всех (с пагинацией)
  - Редактирование (только свой)
  - Мягкое удаление (перемещение в архив `deleted_publications`)
  - Восстановление удалённых
- Просмотр списка удалённых публикаций
- Пагинация списка публикаций
- Отправка приветственного email при регистрации
- Миграции базы данных (Alembic)

#.env файл

POSTGRES_USER=sVlads4

POSTGRES_PASSWORD=simplepass

POSTGRES_DB=marketplace_db

DATABASE_URL=postgresql+asyncpg://sVlads4:simplepass@db:5432/marketplace_db

SECRET_KEY=your-secret-key-here

MAIL_USERNAME=your-email@gmail.com

MAIL_PASSWORD=your-app-password

MAIL_FROM=your-email@gmail.com

MAIL_PORT=587

MAIL_SERVER=smtp.gmail.com

MAIL_TLS=True

MAIL_SSL=False



#API эндпоинты

Метод	Эндпоинт	Описание	Доступ

POST	/auth/register	регистрация	любой

POST	/auth/login	вход (токен)	любой

GET	/auth/me	информация о текущем пользователе	авторизованный

POST	/publication/create	создание публикации	авторизованный

GET	/publication/get_all	список публикаций (пагинация)	любой

GET	/publication/deleted	список удалённых публикаций	любой

PATCH	/publication/edit/{id}	редактирование	только автор

DELETE	/publication/delete/{id}	мягкое удаление	только автор

POST	/publication/restore/{id}	восстановление	только автор

