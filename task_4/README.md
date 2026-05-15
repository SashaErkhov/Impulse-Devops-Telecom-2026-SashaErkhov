# Исправление ошибок в приложении
## Диагностика
Команда `docker logs` показала, что проблема в переменных окружения. В образ забыли перенести апи ключ
## Исправления
Надо добавить в контейнер необходимую переменную окружения. Это можно сделать 1000 и 1 способами. Начиная секретами docker compose или конфиг мапами (ну или опять же секретами) k8s, заканчивая явным объявлением в Dockerfile. Самое простое запустить `docker run` со специальным ключиком:
```shell
docker run -d --name impulse -p 5000:5000 -e API_KEY=ch-me registry.gitlab.com/pulse2026_devops/plaing-with-api_key:latest
```
## Проверка
Это классический X-API-KEY ничего особенного. Вот пример проверки с помощью curl:
```
curl -X GET "http://my-site:5000/process/hello_world" \
     -H "X-API-Key: ch-me" \
     -i
```
Вот такой вывод:
```
Server: Werkzeug/3.1.8 Python/3.12.3
Date: Fri, 15 May 2026 20:47:08 GMT
Content-Type: application/json
Content-Length: 264
Connection: close

{"processed_data":{"is_alnum":false,"is_alpha":false,"is_digit":false,"length":11,"lower":"hello_world","original":"hello_world","reversed":"dlrow_olleh","upper":"HELLO_WORLD"},"processing_time_ms":0.01,"status":"success","timestamp":"2026-05-15T20:47:08.651748"}
```
