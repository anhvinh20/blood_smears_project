# BloodSmears

## Run with Docker (without VS Code)

1. Install [Docker](https://docs.docker.com/get-docker/).
2. Clone this repository:
   ```bash
   git clone git@github.com:anhvinh20/blood_smears_project.git
   cd blood_smears_project
   ```
3. Run : docker build -t bloodsmears .
4. Run : docker run -it --rm -p 8000:8000 bloodsmears
   Access the app at: http://localhost:8000

## Run Locally (without Docker)

1. Clone this repository:
   ```bash
   git clone git@github.com:anhvinh20/blood_smears_project.git
   ```
2. You must dowload : [Python 3.19](https://www.python.org/downloads/release/python-3913/)
3. Open Visual Code and open folder blood_smears_project
4. Run in terminal : pip install --upgrade pip
5. Run in terminal : pip install -r requirements.txt
6. Run in terminal : python app.py
   And access the app at: http://localhost:8000
