import dotenv
import fastapi

dotenv.load_dotenv()

app = fastapi.FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
