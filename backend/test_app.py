import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting test app on port 8000...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
