Simple currency service
===========
Простой сервис для получения информации о курсах валют с [bitfinex.com](https://docs.bitfinex.com/reference).

Cписок доступных валют получает при запуске сервера. В текущей реализации стоит ограничение в 25 видов, т.к. этого достаточно для покрытия текущих требований.


Requirements
------------
Python3.5+


Installation
------------

```shell
    $ pip install -U -r pip-requirements.txt
``` 

Run
---
#### Настройка окружения
Перед запуском необходимо настроить переменные окружения:
* DB_CONNECTION_STR - конфигурация подключения к БД
* DB_MANAGER - используемый менеджер БД. Необязательный параметр. В данный момент реализован только SqlAlchemy. Используется по умолчанию.
```shell
    $ python main.py
```
Сервер будет доступен по адресу `127.0.0.1:1234`

Существующие пользователи указаны в constants.py:AUTH_DICT
***
Доступные методы:
- /update - обновить курсы для существующих валют
- /currencies - получить список существующих валют
- /rate/1 - получить последний курс валюты и среднее значение торгов за последние 10 дней для переданного идентификатора.


