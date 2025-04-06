## Env File
### Add following variabes in .env file:
- `APP_NAME='opensoft'`
- `SUPABASE_URL=`
- `SUPABASE_KEY=`


## A. Setup Server With Poetry

### 1. Install Poetry (if not already)
- `curl -sSL https://install.python-poetry.org | python3 -`

or 

- `sudo apt install python3-poetry`

### 2. (Skip Here) Initialize Poetry project (if needed)
`poetry init`

### 3. Install dependencies from pyproject.toml
`poetry install`

### 4. Run the FastAPI server
`PYTHONPATH=src poetry run uvicorn main:app --reload`

### 5. Installing a new package using poetry:
`poetry add package_name`


## B. API Endpoint Examples (from `/api/activity`)

- `GET http://localhost:8000/activity`  
  → Fetches all activity records.

- `GET http://localhost:8000/activity/EMP0002`  
  → Fetches activity records for employee with ID `EMP0002`.