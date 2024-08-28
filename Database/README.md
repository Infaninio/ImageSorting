# Mariadb Docker Container Readme

## Creating the Mariadb Docker Container

To create a Mariadb Docker container, follow these steps:

1. Open your terminal or command prompt.
2. Run the following command to pull the latest version of the Mariadb Docker image:
```shell
docker pull mariadb:latest
```

## Running the Mariadb Docker Container
Once you have pulled the latest version of the Mariadb Docker image, you can run a container from it using the following command:
```shell
docker run --name mariadb -e MARIADB_ROOT_PASSWORD=mypass -p 3306:3306 -d mariadb:latest
docker update --restart always mariadb
```
This will create a new container named "mariadb-container" and map port 3306 on your host machine to port 3306 in the container.

### Connect via mysql
```shell
mysql -h 172.18.0.2 -P 3306 --protocol=TCP -u root -p
```

### Run sql file in mysql interface
```shell
source Database/schema.sql
```

