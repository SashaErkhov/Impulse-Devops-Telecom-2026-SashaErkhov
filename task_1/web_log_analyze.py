import sys
from datetime import datetime
from pathlib import Path
import re

def file_analyze(filter_date = None):
  access_log = Path("access.log")
  if not access_log.is_file():
    print("=== Ошибка ===")
    print("Файл access.log не найден.")
    exit(1)
  if filter_date is None:
    cnt_filter_date = None
  else:
    cnt_filter_date = 0
  active_ip = dict()
  http_stat = dict()
  http_stat["GET"] = 0
  http_stat["POST"] = 0
  http_stat["PUT"] = 0
  http_stat["DELETE"] = 0
  cnt_errors = 0
  pattern = re.compile(r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) .*? \[(?P<date>.*?)\] "(?P<method>GET|POST|PUT|DELETE|HEAD|PATCH|OPTIONS|CONNECT|TRACE) .*?" (?P<code>\d{3}) (?P<size>\d+)')
  with open(access_log, "r") as f, open("errors.log", "w") as err_f:
    for line in f:
      match = re.match(pattern, line)
      if not match:
        print("=== Ошибка ===")
        print("Неизвестный формат логов.")
        print(f"Не удалось распарсить строку: {line}")
        continue
      ip = match.group("ip")
      date = datetime.strptime(match.group("date"), '%d/%b/%Y:%H:%M:%S %z')
      method = match.group("method")
      status = int(match.group("code"))
      
      if active_ip.get(ip) is None:
        active_ip[ip] = 1
      else:
        active_ip[ip] += 1
      
      # В тз указана статистика только по этим методам
      if method == "GET" or method == "POST" or method == "PUT" or method == "DELETE":
        http_stat[method] += 1

      if status >= 400:
        cnt_errors += 1
        err_f.write(line)
      
      # В тз написано "вывести", но не указано куда.
      # Исходя из примера принято решение просто подсчитать
      # Причем в примере явно видно, что статистика не учитывает дату
      if filter_date is not None and date.date() == filter_date.date():
        cnt_filter_date += 1
  print("=== Топ-3 активных IP ===")
  for ip, cnt in sorted(active_ip.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"{ip}: {cnt} запрос(ов/a)")
  print()
  print("=== Статистика по методам ===")
  for method, cnt in http_stat.items():
    print(f"{method}: {cnt}")
  print()
  print("=== Найдено ошибок (4xx-5xx) ===")
  print(f"Строки с ошибками сохранены в файл errors.log ({cnt_errors} записей)")
  if filter_date is not None:
    print()
    print(f"=== Фильтрация по дате {filter_date.date()} ===")
    print(f"Найдено записей за указанную дату: {cnt_filter_date}")

def main():
  if len(sys.argv) > 2:
    print("=== Ошибка ===")
    print("Невозможное количество аргументов коммандной строки.")
    print("Правильный формат: python web_log_analyze.py [--date=2026-02-16]")
    print("где [] - необязательные аргументы")
    exit(1)
  if len(sys.argv) == 2:
    arg = sys.argv[1]
    if arg[:7] != "--date=":
      print("=== Ошибка ===")
      print(f"Неизвестный аргумент \"{arg}\"")
      print("Правильный формат: python web_log_analyze.py [--date=2026-02-16]")
      print("где [] - необязательные аргументы")
      exit(1)
    try:
      date = datetime.strptime(arg[7:], "%Y-%m-%d")
    except ValueError:
      print("=== Ошибка ===")
      print(f"Неверный формат даты \"{arg[7:]}\"")
      print("Правильный формат: python web_log_analyze.py [--date=2026-02-16]")
      print("где [] - необязательные аргументы")
      exit(1)
    except Exception:
      print("=== Ошибка ===")
      print(f"Неизвестная ошибка при обработке даты \"{arg[7:]}\"")
      print("Правильный формат: python web_log_analyze.py [--date=2026-02-16]")
      print("где [] - необязательные аргументы")
      exit(1)
    file_analyze(date)
  else:
    file_analyze()
    

if __name__ == '__main__':
  main()