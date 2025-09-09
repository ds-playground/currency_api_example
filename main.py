from fastapi import FastAPI
from routers.currency_router import router as currency_router

app = FastAPI()
app.include_router(currency_router)
