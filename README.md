# Image Sorting WebbApp

Image sorting web application using Python and Flask and an sqlite database.

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
