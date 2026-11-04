# Структуры и алгоритмы обработки данных

Вариант 7, seed 37. Каждая папка содержит программу и результаты.

| Работа | Тема | Отчёт |
|---|---|---|
| [ЛР 1](lab01/) | Анализ временной сложности | [Скачать Word](lab01/Otchet_siaod_lab1.docx) |
| [ЛР 2](lab02/) | Рекурсия, массив, стек и дек | [Открыть отчёт](lab02/README.md) |
| [ЛР 3](lab03/) | Сравнение четырёх сортировок | [Открыть отчёт](lab03/README.md) |

Для воспроизведения выполните команды из корня репозитория в Python 3.10 или новее.

~~~sh
python -m pip install -r requirements.txt
python scripts/generate_data.py --variant 7 --only arrays
python scripts/generate_data.py --variant 7 --only ops
python lab01/main.py --variant 7 --out results/lab01
python lab02/main.py --variant 7 --out results/lab02
python lab03/main.py --variant 7 --out results/lab03
~~~

Генератор, каркас проверок и методика эксперимента адаптированы из [материалов МТУСИ](https://github.com/mel0d1an/data-structures-and-algorithms), кафедра «Программная инженерия», 2026. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
