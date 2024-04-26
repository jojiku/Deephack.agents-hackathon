### Для запуска через git clone:
```
git clone https://github.com/jojiku/Deephack.agents-hackathon.git
```
После добавьте файл .env с ключами в формате 

GIGACHAT_API_TOKEN = ...
в главную директорию. 
После 
```
pip install -r requirements.txt
```
### Для запуска через docker перейдите в клонированную папку:
```
cd Deephack.agents-hackathon
```
Далее соберите docker compose:

```
docker-compose build
```
После запустите следующим образом:

```
docker-compose up
```
Сборка занимает 2 минуты
