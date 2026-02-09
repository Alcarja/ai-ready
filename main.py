from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables
from app.routes.itemRoutes import router as itemsRouter
from app.routes.userRoutes import router as usersRouter
from app.routes.userInformationRoutes import router as userInformationRoutes
from app.routes.pdfRoutes import router as pdfRouter
from app.routes.llmRoutes import router as llmRouter
from app.routes.agentRoutes import router as agentRouter

# Define what happens on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code runs here
    create_tables()
    yield
    # Shutdown code runs here (optional)

# Pass the lifespan to FastAPI
app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)

app.include_router(itemsRouter)
app.include_router(usersRouter)
app.include_router(userInformationRoutes)
app.include_router(pdfRouter)
app.include_router(llmRouter)
app.include_router(agentRouter)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
