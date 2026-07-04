"""Clerk JWT authentication for FastAPI."""

from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient, decode as jwt_decode, InvalidTokenError

# Clerk JWKS endpoint (public key for token verification)
CLERK_JWKS_URL = "https://warm-scorpion-21.clerk.accounts.dev/.well-known/jwks.json"

# Clerk issuer (from the `iss` claim in the JWT)
CLERK_ISSUER = "https://warm-scorpion-21.clerk.accounts.dev"

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer(auto_error=False)

# Cached JWKS client (reuses fetched keys)
_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> PyJWKClient:
    """Get or create a cached JWKS client."""
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(CLERK_JWKS_URL, cache_keys=True)
    return _jwks_client


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency that optionally verifies the Clerk JWT.
    
    If a valid Bearer token is provided, returns the user ID.
    If no token is provided or token is invalid, returns "anonymous".
    Never raises 401 — for endpoints where auth is optional.
    """
    if credentials is None:
        return "anonymous"

    token = credentials.credentials
    if not token:
        return "anonymous"

    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt_decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["sub", "exp"],
            },
        )

        iss = payload.get("iss", "")
        if iss != CLERK_ISSUER and not iss.endswith(".clerk.accounts.dev"):
            return "anonymous"

        user_id = payload.get("sub")
        if not user_id:
            return "anonymous"

        return user_id

    except Exception:
        return "anonymous"


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency that REQUIRES a valid Clerk JWT.
    
    Raises 401 if the token is missing or invalid.
    Used for endpoints that need guaranteed authentication (contract listing).
    """
    # Allow public endpoints
    public_paths = {"/", "/docs", "/openapi.json", "/api/v1/health", "/redoc"}
    if request.url.path in public_paths:
        return "anonymous"

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide a Bearer token.",
        )

    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token.")

    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt_decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["sub", "exp"],
            },
        )

        iss = payload.get("iss", "")
        if iss != CLERK_ISSUER and not iss.endswith(".clerk.accounts.dev"):
            raise HTTPException(status_code=401, detail=f"Invalid token issuer: {iss}")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing 'sub' claim.")

        return user_id

    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")