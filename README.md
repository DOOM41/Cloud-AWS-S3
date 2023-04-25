BACKEND: <br>
    - [x] [FASTAPI](https://fastapi.tiangolo.com/)<br>
    ENDPONTS:<br>
        - [POST] /upload - form-data<br>

FRONTEND:<br>
    HTML/CSS/JS <br>


NEW: <br>
    Реализовал отправку файлов со строноны фронта по частям и сразу отправляю эти части с бэка на AWS S3, с помощью библиотеки boto3.<br>

    Для запуска проекта необходимо:
        1. Создать виртуальное окружение и активировать его
        2. Установить зависимости из requirements.txt
        3. Запустить проект командой: uvicorn main:app --reload либо "py .\BackEnd\main.py"
        4. И открыть index.html



OLD:
    P.S. Сделал две вариации отправки файла на AWS S3, одна через встроенный метод библиотеки boto3 в файле utils.py, 
    вторая уже кастомно используя методы отправки upload_part с помощью библиотеки concurrent.futures в файле second_util_v.py.

    В файле main.py:
    from utils import run_in_thread -> первый вариант

    from second_util_v import run_in_thread -> второй вариант
