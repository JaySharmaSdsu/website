import fastapi as _fastapi
import fastapi.encoders as _encoders
import fastapi.responses as _responses


import services as _services

from fastapi.middleware.cors import CORSMiddleware

app = _fastapi.FastAPI()

# Allow CORS for port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/memes")
def get_cat_memes():
    image_path = _services.select_image()
    return _responses.FileResponse(image_path)


