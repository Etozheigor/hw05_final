# Yatube

### О проекте

Данный проект является солиальной сетью-дневником для блоггеров. Дает возможность публиковать посты, подписываться на других пользователей, ставить лайки. Можно просматривать посты в общей ленте новостей, в ленте своих подписок или в тематических группах.

### Технологии
- Python
- Django
- HTML
- CSS

### Как запустить проект:

- Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Etozheigor/hw05_final.git
```

```
cd hw05_final
```

- Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

- Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

- Выполнить миграции:

```
python manage.py migrate
```

- Запустить проект:

```
python manage.py runserver
```

Проект будет доступен локально по адресу:

```
http://localhost/
```
