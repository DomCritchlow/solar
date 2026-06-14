# Solar Monitor

A small FastAPI application that retrieves solar data from NOAA's SWPC APIs and renders a simple web page. Data is cached for five minutes and demo data is used when the remote service is unavailable.

## Running the app

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Visit `http://localhost:8000` to see the rendered page or access `/api/solar-data` for the JSON payload.
