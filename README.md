# Image Sorting WebbApp

Image sorting web application using Python and Flask and an sqlite database.

## General Setup
Use a `.env` file to store your environment variables. The `.env` file should contain the following:
```shell
NEXTCLOUD_URL="https://cloud.nextcloud.de"
NEXTCLOUD_USER="user"
NEXTCLOUD_PASSWORD="asdf"
IMAGE_SORT_DEBUG=True
```


## SetUp in Container
To follow along you need to install python, pip virtualenv and git in the container.

### Setup Project
#### Create Database with
```shell
python ./Database/create_database.py
```

#### Create cron job for update database with new images.
First setup the necessary environment variables
```shell
export NEXTCLOUD_URL='https://cloud.yourDomain.com'
export NEXTCLOUD_USER='martin'
export NEXTCLOUD_PASSWORD='asdf1234'

chmod +x WebUI/search_images.py
```

#### Edit crontab
```shell
crontab -e
0 1 * * * /bin/sh -c 'source ~/ImageSorting/.venv/bin/activate && cd ~/ImageSorting && ~/ImageSorting/.venv/bin/python3 -m WebUI.search_images >> /var/log/cron.log 2>&1'
```

## Project Structure

### Database
Contains all scripts for setting up the database, including creating tables and inserting initial data.
The initial data is only used for testing.

To create the database run:

```shell
python ./Database/create_database.py
```

### WebUI
Contains the Flask web application code.

Run the application using
```shell
cd WebUI
python -m flask run --host=0.0.0.0 --port=5000
```

### Image finder
Search for images in your Nextcloud with

```shell
python -m WebUI.search_images
```

## Development

### [Optional] Install virtual environment
```shell
python -m venv .venv
```

### Use pre-commit hooks

Install with

```shell
pip install pre-commit # Included in requirements.txt
```

Initial run with
```shell
pre-commit install
```

(Optional) Run against all files
```shell
pre-commit run --all-files
```

### Setup a dev environment

A small debug server can be setup with this script.
```shell
python -m WebUI.setup_dev_env --image-dir /folder/with/some/pictures --nr_images 1000
# The number of images must not equal the number of pictures in the folder.
# It will repeat if necessary the images from the folder.
```
The script adds `User1`, `User2`, `User3` as users with password `password`.
The useres have different access to the different collections.


Afterwards start the server with:
```shell
cd WebUI
python -m flask run --host=0.0.0.0 --port=5000 --debug
# The --debug enables the loading from a local storage.
```
