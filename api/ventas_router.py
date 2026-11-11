"""Router de Ventas. Los endpoints se agregan al implementar cada historia de usuario."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Ventas"])
