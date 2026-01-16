from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from typing import Optional, Any

from app.services.absa_service import analyze_items
from app.utils.errors import UpstreamQuotaError

import logging

log = logging.getLogger(__name__)

router = APIRouter()


@router.post('/analyze')
async def analyze(request: Request, text: Optional[str] = Form(None), upload_file: Optional[UploadFile] = File(None)):
    """
    Performs analysis on text or file upload.

    Args:
        request (Request): FastAPI request object.
        text (Optional[str]): Text to be analyzed.
        upload_file (Optional[UploadFile]): CSV file containing data to be analyzed.

    Returns:
        A JSON object containing the analysis results.

    Raises:
        HTTPException: If the input is invalid or an upstream error occurs.
    """
    payload: Any = None

    if upload_file is not None:
        filename = getattr(upload_file, 'filename', None)
        log.info("Received analyze request with file upload filename=%s", filename)
        if not filename or not filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail='Sadece CSV dosyası yükleyin (.csv).')
        payload = upload_file
    elif text:
        log.info("Received analyze request with text input")
        payload = text
    else:
        raise HTTPException(status_code=400, detail='İstek ya tek satır metin (`text`) ya da CSV dosyası (`upload_file`) içermeli.')

    try:
        log.info("Starting analysis...")
        result = await analyze_items(payload)
        log.info("Analysis completed successfully")
        return result
    except UpstreamQuotaError as e:
        raise HTTPException(status_code=429, detail={
            'error': 'Upstream kotası aşıldı veya rate-limit alındı',
            'message': 'Model sağlayıcısından kotaya ilişkin bir hata döndü. Lütfen daha sonra tekrar deneyin.',
            'upstream_error': str(e),
        })
