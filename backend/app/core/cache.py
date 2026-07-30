import asyncio
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class AsyncCache:
    """
    Caché asíncrono seguro para entornos concurrentes.
    Usa un lock para evitar condiciones de carrera al escribir.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor si existe y no ha expirado."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry["expires_at"] > datetime.now():
                    return entry["value"]
                else:
                    # Limpieza automática si expiró
                    del self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Guarda un valor con un tiempo de vida (TTL) en segundos."""
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        async with self._lock:
            self._cache[key] = {"value": value, "expires_at": expires_at}

    async def clear(self) -> None:
        """Limpia todo el caché."""
        async with self._lock:
            self._cache.clear()


# Instancia global única
cache = AsyncCache()
