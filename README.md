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
- Detail pages available by /api/airport/"number"/"names"/

# Project pages
Crews: ![image](https://github.com/IvanMozhar/airport-service/assets/147508342/a4d043ca-0657-4af0-84b2-624a7afeea30)
Airports: ![image](https://github.com/IvanMozhar/airport-service/assets/147508342/96800435-0b29-4da7-8b83-807dfde11e60)
Routes: ![image](https://github.com/IvanMozhar/airport-service/assets/147508342/1dd07917-a4b9-48dd-8f5c-ce626b29977f)
Airplane types: ![image](https://github.com/IvanMozhar/airport-service/assets/147508342/eedcf932-89b3-4055-82f2-d29ba8fe46ba)
Flights: ![image](https://github.com/IvanMozhar/airport-service/assets/147508342/ea5d156f-1a80-43a2-97ac-deea3d782255)
