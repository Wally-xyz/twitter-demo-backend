# wally-api
Primary API Repo 


### How to get this running
Clone this repository
Run `pip install -r requirements.txt`
Run `uvicorn app.src.main:app --host=0.0.0.0 --port=80 --reload`
Navigate to `http://127.0.0.1/docs`


### To Setup the Postgres Database:
Install Postgres on your computer (I Used the Postgres.app)
`psql` into the local database
- Create the Wally database: `CREATE DATABASE wally_api;`
- Create the Wally API user, pull the password from SSM:
- `aws ssm get-parameter --name=/dev/api/db_password`
- `create user wally_api_user with password 'password';` 
- Grant permissions to that user
- `alter user wally_api_user with superuser;`
- Exit the PSQL Client. 
- [Run the Alembic migrations](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration):
- `alembic upgrade head`
- You should now be ready to run the application!


### Authentication
##### TODO


### If you want to run this in python/pycharm/debugger...?
Uncomment out the `if __name__ == "__main__"` piece in `main.py`.
Might have issues with imports though


### To run this locally via docker:
- `docker build -t myimage_gunicorn .`
- `docker run -v $HOME/.aws/credentials:/root/.aws/credentials:ro -d --name mycontainer1 -p 80:80 myimage_gunicorn`


### To run this locally with Uvicorn:
`uvicorn app.src.main:app --host=0.0.0.0 --port=80 --reload`


