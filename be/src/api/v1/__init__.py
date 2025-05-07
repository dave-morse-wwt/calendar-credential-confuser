from fastapi import APIRouter

from . import auth, google

router = APIRouter()
router.include_router(auth.router)
router.include_router(google.router)
