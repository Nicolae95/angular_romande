# Start the server (it is necesary to have docker installed on your machine)

The comands a necessary to introduce in ./server directory
1. docker-compose run server python src/conversion_tool/manage.py migrate
2. docker-compose run server python src/conversion_tool/manage.py collectstatic --noinput
3. docker-compose run server python src/conversion_tool/manage.py createsuperuser
4. docker-compose up

To start the client (client directory)
1. npm install
2. ng serve