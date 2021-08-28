from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .accounts import router as acct_router
from .transactions import router as trans_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(acct_router)
app.include_router(trans_router)