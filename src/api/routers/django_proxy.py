"""
Proxy router para redirigir peticiones del marketplace a Django
"""
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

DJANGO_BASE_URL = "http://localhost:8001"

@router.api_route("/marketplace/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_django(path: str, request: Request):
    """
    Proxy todas las peticiones /marketplace/* a Django
    """
    # Construir URL completa de Django
    django_url = f"{DJANGO_BASE_URL}/marketplace/{path}"
    
    # Obtener query params
    query_params = dict(request.query_params)
    
    # Obtener headers (excepto host)
    headers = dict(request.headers)
    headers.pop('host', None)
    
    logger.info(f"🔄 Proxying {request.method} {django_url}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Obtener el body si existe
            body = await request.body()
            
            # Hacer la petición a Django
            response = await client.request(
                method=request.method,
                url=django_url,
                params=query_params,
                headers=headers,
                content=body,
                cookies=request.cookies
            )
            
            logger.info(f"✅ Django responded with status {response.status_code}")
            
            # Retornar la respuesta de Django
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get('content-type')
            )
            
    except httpx.TimeoutException as e:
        logger.error(f"⏱️ Timeout proxying to Django: {e}")
        return Response(
            content="Request timeout - Django server took too long to respond",
            status_code=504
        )
    except httpx.RequestError as e:
        logger.error(f"❌ Error proxying to Django: {e}")
        return Response(
            content=f"Error connecting to Django: {str(e)}",
            status_code=502
        )
