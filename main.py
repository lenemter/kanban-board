import db
import dotenv
import fastapi

dotenv.load_dotenv()

db.create_db_and_tables()

app = fastapi.FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
