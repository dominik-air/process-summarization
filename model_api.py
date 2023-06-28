import os
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="website"), name="static")


def read_models(dir: str) -> dict[str, str]:
    models = {}
    for i, file in enumerate(os.listdir(dir)):
        with open(f"{dir}/{file}") as f:
            models[f"model{i}"] = "".join(f.readlines()).strip()
    return models


models = read_models(dir="website/models")


@app.get("/models")
async def get_models():
    return {"models": [{"name": key, "url": f"/models/{key}"} for key in models.keys()]}

@app.get("/models/{model_id}")
async def get_model(model_id: str):
    if model_id not in models:
        return {"detail": f"Model with id: {model_id} not found"}

    return Response(content=models[model_id], media_type="application/xml")
