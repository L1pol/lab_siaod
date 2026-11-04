# Структуры и алгоритмы обработки данных

Вариант 7, seed 37. Каждая папка содержит программу и результаты.

| Работа | Тема | Отчёт |
|---|---|---|
| [ЛР 1](lab01/) | Анализ временной сложности | [Скачать Word](lab01/Otchet_siaod_lab1.docx) |
| [ЛР 2](lab02/) | Рекурсия, массив, стек и дек | [Word](lab02/Otchet_siaod_lab2.docx) · [Онлайн](lab02/README.md) |
| [ЛР 3](lab03/) | Сравнение четырёх сортировок | [Word](lab03/Otchet_siaod_lab3.docx) · [Онлайн](lab03/README.md) |
| [ЛР 4](lab04/) | Слияние, подсчёт, поразрядная сортировка и куча | [Word](lab04/Otchet_siaod_lab4.docx) · [Онлайн](lab04/README.md) |
| [ЛР 5](lab05/) | Бинарное дерево поиска | [Word](lab05/Otchet_siaod_lab5.docx) · [Онлайн](lab05/README.md) |
| [ЛР 6](lab06/) | Поиск ключа в массиве | [Word](lab06/Otchet_siaod_lab6.docx) · [Онлайн](lab06/README.md) |
| [ЛР 7](lab07/) | Поиск подстроки | [Word](lab07/Otchet_siaod_lab7.docx) · [Онлайн](lab07/README.md) |
| [ЛР 8](lab08/) | Хеш-таблица с цепочками | [Word](lab08/Otchet_siaod_lab8.docx) · [Онлайн](lab08/README.md) |

Для воспроизведения выполните команды из корня репозитория в Python 3.10 или новее.

~~~sh
python -m pip install -r requirements.txt
python scripts/generate_data.py --variant 7 --only arrays
python scripts/generate_data.py --variant 7 --only ops
python lab01/main.py --variant 7 --out results/lab01
python lab02/main.py --variant 7 --out results/lab02
python lab03/main.py --variant 7 --out results/lab03
python lab04/main.py --variant 7
python lab05/main.py --variant 7
python lab06/main.py --variant 7
python lab07/main.py --variant 7
python lab08/main.py --variant 7
~~~

Генератор, каркас проверок и методика эксперимента адаптированы из [материалов МТУСИ](https://github.com/mel0d1an/data-structures-and-algorithms), кафедра «Программная инженерия», 2026. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
