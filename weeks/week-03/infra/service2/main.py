from fastapi import FastAPI

app = FastAPI(title="Other")

@app.get("/other")
async def get_other():
    return {
        "message": "Это второй сервис",
        "service": "service2"
    }
