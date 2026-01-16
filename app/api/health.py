from fastapi import APIRouter
import time

router = APIRouter()


@router.get('/health')
async def health():
    return {
        'status': 'ok',
        'timestamp': time.time()
    }


@router.get('/ready')
async def ready():
    """
    Checks if the application is ready.
    """
    return {
        'ready': True
    }


__all__ = ['router']
