# Тестовое задание bewise.ai
https://docs.google.com/document/d/1Xw4L-_riLixQFA127Uyvoq3JNrJm6hgSr7c7ux6z_fY/edit#

Для первого задания реализовать сервис, который принимает на вход целое число n, отправляет его на сторонний API, получает n вопросов для викторин, сохраняет их в БД и возвращает последний сохраненный

Для второго сделать сервис, который будет создавать пользователя с uuid токеном. Пользователь дает свой токен, id и аудиофайл в .wav формате. Приложение конвертирует его в .mp3 и сохраняет файл в БД, возвращая ссылку для скачивания

Инструкция по сборке каждого из тестовых:

    1. Зайти в директорию нужного сервиса (типа cd task_1/task_2).
    2. Изнутри прописать "docker-compose up -d"
    3. После сборки зайти в контейнер, где расположен flask сервер
    4. Поочередно прописать "flask db init", "flask db migrate", "flask db upgrade"

## Запросы для task_1
**Тело запроса должно иметь вид "*{'question_num': int}*"**

Пример с использованием cURL: 
    
    curl -X POST localhost:5000 -d "{'question_num': '1'}"
    curl -X POST localhost:5000 -d "{\"question_num\": \"1\"}" - если cmd в Windows

## Запросы для task_2
### **index route** (там создаем пользователя)
Подавать *{"username": str}*

    curl -X POST localhost:5000 -d "{'username': 'foo'}" 

### **upload route**
    curl -X POST -H "Content-Type: multipart/form-data" \ 
    -F "file=@path/to/file.wav" \ 
    -F "user_id=1" \
    -F "uuid_token=token" \
    http://localhost:5000/upload

### **record route**
Ну тут просто воспользоваться ссылкой полученной с upload'а