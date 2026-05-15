# Оптимизация Dockerfile
## Старый файл
```Dockerfile
FROM python:3.12
RUN mkdir /app
RUN mkdir /app/src
RUN mkdir /app/logs
RUN mkdir /app/temp
COPY . /app/
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install requests
RUN pip install flask
RUN pip install pandas
RUN pip install numpy
RUN pip install gunicorn
RUN apt-get update
RUN apt-get install -y wget
RUN wget https://example.com/some-tool.tar.gz
RUN tar -xzf some-tool.tar.gz
RUN mv some-tool /usr/local/bin/
RUN rm some-tool.tar.gz
COPY config.yaml /app/config.yaml
COPY data/ /app/data/
RUN apt-get install -y curl
RUN apt-get install -y nano
RUN python -m venv /opt/venv
RUN rm -rf /root/.cache/pip
RUN rm -rf /app/temp/*
RUN rm -f /app/*.tar.gz
RUN rm -f /app/*.log
CMD ["python", "/app/src/app.py"]
```
## Оптимизация
### Образ
```Dockerfile
FROM python:3.12 
```
Образ слишком общий - в этом есть ряд проблем.  
 1. Недетерминированное поведение приложения: при обновлении новой минорной версии образа может измениться его внутреннее содержимое, что негативно может сказаться на итоговом продукте
 2. Излишнее использование памяти. При каждом обновлении образа при сборке он будет скачиваться, что приведет к накапливанию лишних слоев. Самое грустное, что это обычно обнаруживается поздно (так же как и в случае отсутствия ограничений на память логов в докере), скажем через лет 7  

Рекомендация: либо использовать очень точный образ со всеми минорными образами, скажем, еще и легковесный: `FROM python:3.12.3-slim` (Если есть возможность, можно зафиксировать еще и версию slim), либо использовать собственные докер регистри только с заранее скачиванными обазами (это даст еще и бонус в безопасность, так как обзары можно проверить заранее и их нельзя будет подменить извне)
### Слоистость
В образе каждое действие пишется отдельной командой, что очень раздувает образ. Пример прикреплять не буду, это повсеместная проблема
### mkdir
```Dockerfile
RUN mkdir /app
RUN mkdir /app/src
RUN mkdir /app/logs
RUN mkdir /app/temp
```
Это вообще глупость, лишние команды. Команда COPY сама создает отсутствующие директории. (Они бы пригодились, если мы что-то прям в образе туда заносили, при том, что эти директории отсутствуют при создании образа вне образа - но по остальному содержимому видно, что это не так)
### COPY all
```Dockerfile
COPY . /app/
```
Это нормально только в том случае, если адекватно настроен файл `.dockerignore`. Буду предполагать, что это так. Таким образом, следущая команда `COPY requirements.txt /app/requirements.txt` бесполезна (как и другие копирования далее)
### big installing
```Dockerfile
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install requests
RUN pip install flask
RUN pip install pandas
RUN pip install numpy
RUN pip install gunicorn
```
Необходимо все эти пакеты записать в `requirements.txt`, если их там еще нет, причем с зафиксированными версиями. Таким образом это превращается в одно команду
```Dockerfile
RUN pip install --no-cache-dir -r /app/requirements.txt
```
### install curl и nano
Эти команды далее в образе не используются, но предполагая, что это нужно для ручной отладки и работы в дальнейшем, я это оставил
### new venv
Это бесполезная команда, удаляем
### rm -rf
 - cache - Вы эту директорию и не создавали, удаляем
 - temp, *.log - Мы с ними в процессе создания образа не работали. Предполагая, что `.dockerignore` работает корректно, эти команды не нужны
 - *.tar - мы все уже удалили таргетно
## Итоговый файл:
```Dockerfile
FROM python:3.12.3-slim
COPY . /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN apt-get update && \
  apt-get install -y wget curl nano
RUN wget https://example.com/some-tool.tar.gz && \
  tar -xzf some-tool.tar.gz && \
  mv some-tool /usr/local/bin/ && \
  rm some-tool.tar.gz
CMD ["python", "/app/src/app.py"]
```