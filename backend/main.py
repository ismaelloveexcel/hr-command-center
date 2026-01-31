from fastapi import FastAPI

app = FastAPI(title="UAE HR Portal API")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
