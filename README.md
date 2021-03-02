# Backend Stack

* Python 3.8+
* [FastAPI]
* [PostgreSQL 12/13]
* [SQLAlchemy]
* [Redis]


## Quickstart

##### Install Python Dependencies

Install required python packages. Create a virtual environment (`python3 -m venv venv`, then `source venv/bin/activate`. From this directory (`/backend`) run the following command:

		pip3 install -r requirements.txt
		
For SAML auth, we also need to install some system packages. 

On Ubuntu:

```
apt-get install libffi-dev xmlsec1 libxmlsec1-openssl
```

Mac/Homebrew:
```
brew install xmlsec1
```

##### Start Webserver

To start the webserver, run [uvicorn](https://www.uvicorn.org/) from the `backend` directory with the following command:

		$ uvicorn app.main:app --reload
		
Here, `app.main` is the path to the `main.py` source file and `:app` is the name of the FastAPI webserver defined in that file.
## Style Guidelines and Linting

Code style is being enforced with [black](https://github.com/psf/black) and linting is being done with [pylint](https://github.com/PyCQA/pylint).


## Testing

Tests are implemented using `pytest`. Run them with the following command:

		$ pytest app
