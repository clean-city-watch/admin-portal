# admin-portal-backend

Clone the repository to your local machine:
```bash
git clone https://github.com/clean-city-watch/admin-portal.git
```
To run the FASTAPI Application use the following command:

```bash
uvicorn main:app --reload
```

# Endpoints
Once the application is running, you can access its endpoints by visiting the Swagger documentation at http://localhost:8000/docs or the ReDoc documentation at http://localhost:8000/redoc.


# running on server
SSH into the server, copy or clone the repo there.  
Ensure the .env file is present in folder on server. 

Install python libs needed:
```
pip install -r requirements.txt
```

Make launch shell script executable:
```
chmod +x ./server_launch.sh
```

Start the program
```
nohup ./serverserver_launch.sh &
```
- "&" : means it will run in background
- "nohup" : means program will continue running even after you have logged off from your ssh session

