# Airport service
The Airport Service API is a system designed to manage various aspects of airline 
operations and services. This API facilitates a wide range of functionalities 
from managing crew details, airports, flight routes, airplane types, 
and airplanes themselves to handling orders, flights, and ticketing.
## Installing using GitHub
Install PostgresSQL and create database

```
git clone https://github.com/IvanMozhar/airport-service.git
cd airport_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set DJANGO_SECRET_KEY=<yoursecretkey>
set POSTGRES_HOST=<your db host name>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=<your db password>
python manage.py migrate
python manage.py runserver
```

# Run with Docker
Install and create account in Docker first
```
docker-compose build
docker-compose up
```
### Pull from docker
```
docker pull ivanmozhar/airport_service-app:latest
```

## To get access
- create user via /api/user/register/
- get access token via /api/user/token/

# Project features
- Admin panel /admin/
- JWT authentication
- Documentation: /api/doc/swagger
- Create crews, airports, airplanes, routes, flights
- Manage tickets and orders
