import dotenv
from fastapi import FastAPI

import api.db
import api.routers

dotenv.load_dotenv()

api.db.create_db_and_tables()

app = FastAPI()
app.include_router(api.routers.auth_router)
app.include_router(api.routers.users_router)
app.include_router(api.routers.boards_router)
app.include_router(api.routers.columns_router)
app.include_router(api.routers.tasks_router)
