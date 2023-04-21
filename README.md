BACKEND: 
    - [x] [FASTAPI](https://fastapi.tiangolo.com/)
    ENDPONTS:
        - [POST] /upload - form-data

FRONTEND:
    HTML/CSS/JS 


P.S. Сделал две вариации отправки файла на AWS S3, одна через встроенный метод библиотеки boto3 в файле utils.py, 
вторая уже кастомно используя методы отправки upload_part с помощью библиотеки concurrent.futures в файле second_util_v.py.

from utils import run_in_thread -> первый вариант

from second_util_v import run_in_thread -> второй вариант