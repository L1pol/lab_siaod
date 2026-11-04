# Структуры и алгоритмы обработки данных

Вариант 7, seed 37. Для запуска нужен Python 3.10 или новее. Команды выполняются из корня репозитория.

~~~sh
python -m pip install -r requirements.txt
python scripts/generate_data.py --variant 7 --only arrays
python scripts/generate_data.py --variant 7 --only ops
python main.py --variant 7 --out results/lab01
python lab02/main.py --variant 7 --data data/generated --out results/lab02
~~~

Каждая программа проверяет реализации до начала замеров. Для ЛР 1 используйте обычный запуск Python, чтобы работали проверки assert. Повторные запуски сохраняют графики в указанные каталоги.

* **ЛР 1. Анализ сложности** — [программа](main.py), [отчёт](Otchet_siaod_lab1.docx), [степенные зависимости](lab01_loglog.png), [бинарное возведение в степень](lab01_binary_pow.png).
* **ЛР 2. Рекурсия и линейные структуры** — [программа](lab02/main.py), [отчёт с графиками](lab02/README.md).

Генератор, основа самопроверок и методика измерений взяты из [репозитория курса МТУСИ](https://github.com/mel0d1an/data-structures-and-algorithms). В заготовки добавлены реализации и проверки. © МТУСИ, кафедра «Программная инженерия», 2026. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
