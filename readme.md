# Cafebabel


## Installation


### Requirements

Python 3.6+


## Preparing the project

```
python3 -m venv ./venv
source ./venv/bin/activate
```

### Installing the dependencies

```
export FLASK_APP=cafebabel
export FLASK_DEBUG=1
pip install -e .
```

### Installing the database

```
flask initdb
```

> You may reset your database by deleting the _/cafebabel.db_ file and
re-initializing the database.

### Configuring

If existing, the file `settings.local.py` at the root of the project will
override the default `settings.py` configuration.


## Running the project

```
flask run
```


## Running a dummy mail server

```
sudo python -m smtpd -n -c DebuggingServer localhost:25
```


## Production installation

In order to deploy to the staging server, you should have an SSH access
to the server with the _cafebabel_ user callable via the command `ssh cafebabel`.

Your server must have python3.6 installed.

Installation can be processed with `make install`.
Deploying will run through `make deploy`.
