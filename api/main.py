import dotenv
from fastapi import FastAPI

import api.db
import api.routers.auth
import api.routers.users

dotenv.load_dotenv()

api.db.create_db_and_tables()

app = FastAPI()
app.include_router(api.routers.auth.router)
app.include_router(api.routers.users.router)
