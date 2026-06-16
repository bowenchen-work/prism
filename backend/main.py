from fastapi import FastAPI

app = FastAPI(title="Prism API")

@app.get("/health")
def health():
    return {"status": "ok"}