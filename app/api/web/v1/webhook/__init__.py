from fastapi import APIRouter

from . import payment


router = APIRouter()


router.include_router(payment.router, tags=["Payment"], prefix="/payment")
