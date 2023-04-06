## Ruslanbers - социальная сеть для блоггеров
### Описание
Мини-социальная сеть для ведения блога: посты, комментарии к ним, лайки, подписки  
### Используемые технологии:
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![image](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![image](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![image](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
### Доступные возможности
##### Заложено по ТЗ заказчика (Яндекс Практикум):
- Страницы: главная, страница сообщества, профайл автора с постами, карточка поста
- Создание и редактирование постов
- Создание комментариев к посту
- Работа с сообществами (создание через админ-панель и его опциональный выбор в посте)
- Возможность подписок на авторов (лента подписки с переключателем на главную страницу)
- Возможность добавления картинок к постам
- Настроенная админ-панель
- Работа с пользователями: регистрация новых, вход/выход, смена пароля и восстановление пароля (эмулятор)
##### Реализовано помимо пожеланий заказчика из ЯП:
- Страницы: навигация по группам и авторам с авторами-лидерами по постам и комментариям
- Личный кабинет с полями за рамками стандартной модели (аватары, доп.инфо об авторе)
- Пользовательские и стандартные аватары
- Удаление постов и комментариев
- Система лайков понравившимся постам
- Отражение информации о лайках и комментариях в лентах постов с рабочими ссылками
- Поиск в постах по ключевым словам
- Система тегов для навигации по постам в виде разноцветных кнопок
- Немного красоты: кнопки действий вместо ссылок, картинки к кнопкам, посты в виде карточек, оптимизация для различных устройств

![image](https://github.com/ratarov/ruslanbers/raw/master/yatube/static/img/1.png)
![image](https://github.com/ratarov/ruslanbers/raw/master/yatube/static/img/2.png)
![image](https://github.com/ratarov/ruslanbers/raw/master/yatube/static/img/3.png)

### Установка
**Как запустить проект:**
```
>>> Клонировать репозиторий и перейти в него в командной строке:
git clone https://github.com/ratarov/ruslanbers_social_network
cd yatube
```
```
>>> Cоздать и активировать виртуальное окружение:
py -m venv venv (для Windows) /python3 -m venv venv (для MacOS)
source venv/bin/activate (для Windows) / source venv/bin/activate (для MacOS)
```
```
>>> Установить зависимости из файла requirements.txt:
python -m pip install --upgrade pip (MacOS python3 -m pip install --upgrade pip для MacOS)
pip install -r requirements.txt (python3 pip install -r requirements.txt для MacOS)
```
```
>>> Выполнить миграции:
python manage.py migrate (если вы пользователь MacOS python3 manage.py migrate)
```
```
>>> Запустить проект:
python manage.py runserver (если вы пользователь MacOS python3 manage.py runserver)
```