import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlsplit
from uuid import uuid4

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.models.schemas import ApiResponse, LinkedInStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])

AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"


def _fernet() -> Fernet:
    if not settings.LINKEDIN_TOKEN_ENCRYPTION_KEY:
        raise HTTPException(
            status_code=503,
            detail="LinkedIn token encryption is not configured",
        )
    try:
        return Fernet(settings.LINKEDIN_TOKEN_ENCRYPTION_KEY.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise HTTPException(
            status_code=503,
            detail="LINKEDIN_TOKEN_ENCRYPTION_KEY must be a valid Fernet key",
        ) from exc


def _connection() -> dict | None:
    row = db.fetch_one(
        "SELECT * FROM linkedin_connections WHERE user_id = ?",
        (DEFAULT_USER_ID,),
    )
    return row


def _connection_token(row: dict) -> str:
    try:
        return _fernet().decrypt(row["encrypted_token"].encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeEncodeError) as exc:
        logger.error("Stored LinkedIn access token could not be decrypted")
        raise HTTPException(
            status_code=503,
            detail="Saved LinkedIn connection cannot be decrypted; reconnect LinkedIn",
        ) from exc


def _linkedin_http_error(response: httpx.Response) -> HTTPException:
    logger.warning("LinkedIn request failed with HTTP %s", response.status_code)
    if response.status_code in (401, 403):
        return HTTPException(
            status_code=502,
            detail="LinkedIn rejected the connection or publishing permission; reconnect or check app access",
        )
    return HTTPException(
        status_code=502,
        detail=f"LinkedIn request failed with HTTP {response.status_code}",
    )


@router.get("/status", response_model=ApiResponse[LinkedInStatus])
def get_linkedin_status():
    row = _connection()
    expires_at = row["expires_at"] if row else None
    configured = bool(
        settings.LINKEDIN_CLIENT_ID
        and settings.LINKEDIN_CLIENT_SECRET
        and settings.LINKEDIN_TOKEN_ENCRYPTION_KEY
    )
    connected = bool(
        configured
        and row
        and expires_at
        and expires_at > datetime.now(timezone.utc).isoformat()
    )
    return ApiResponse(
        success=True,
        data=LinkedInStatus(
            configured=configured,
            connected=connected,
            member_name=row["member_name"] if connected else None,
            expires_at=expires_at,
            expected_profile_url="https://www.linkedin.com/in/tilakc623/",
        ),
    )


@router.get("/connect")
def connect_linkedin():
    if not settings.LINKEDIN_CLIENT_ID or not settings.LINKEDIN_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Configure the LinkedIn Developer app client ID and secret first",
        )
    _fernet()
    state = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(minutes=10)).isoformat()
    db.execute(
        "DELETE FROM linkedin_oauth_states WHERE expires_at <= ?",
        (now.isoformat(),),
    )
    db.execute(
        "INSERT INTO linkedin_oauth_states (state, user_id, expires_at) VALUES (?, ?, ?)",
        (state, DEFAULT_USER_ID, expires_at),
    )
    query = urlencode({
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": "openid profile w_member_social",
        "state": state,
    })
    return RedirectResponse(f"{AUTHORIZATION_URL}?{query}", status_code=303)


@router.get("/callback")
def linkedin_callback(
    code: str | None = Query(default=None, max_length=4096),
    state: str | None = Query(default=None, max_length=256),
    error: str | None = Query(default=None, max_length=256),
):
    callback_url = f"{settings.LINKEDIN_FRONTEND_URL.rstrip('/')}/?linkedin="
    if error:
        return RedirectResponse(callback_url + "denied", status_code=303)
    if not code or not state:
        raise HTTPException(status_code=400, detail="LinkedIn OAuth response is missing code or state")

    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        state_row = conn.execute(
            "SELECT state, user_id, expires_at FROM linkedin_oauth_states WHERE state = ?",
            (state,),
        ).fetchone()
        if not state_row:
            conn.commit()
            raise HTTPException(status_code=400, detail="LinkedIn OAuth state is invalid or expired")
        if (
            state_row["expires_at"] <= datetime.now(timezone.utc).isoformat()
            or not secrets.compare_digest(state, state_row["state"])
        ):
            conn.execute("DELETE FROM linkedin_oauth_states WHERE state = ?", (state,))
            conn.commit()
            raise HTTPException(status_code=400, detail="LinkedIn OAuth state is invalid or expired")
        conn.execute("DELETE FROM linkedin_oauth_states WHERE state = ?", (state,))
        conn.commit()
        state_row = dict(state_row)

    try:
        token_response = httpx.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
            timeout=15.0,
        )
        if token_response.status_code != 200:
            raise _linkedin_http_error(token_response)
        token_data = token_response.json()
        access_token = token_data["access_token"]
        expires_in = int(token_data["expires_in"])
        userinfo_response = httpx.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15.0,
        )
        if userinfo_response.status_code != 200:
            raise _linkedin_http_error(userinfo_response)
        userinfo = userinfo_response.json()
        person_id = userinfo["sub"]
        member_name = userinfo.get("name")
    except HTTPException:
        raise
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        logger.warning("LinkedIn OAuth exchange failed: %s", type(exc).__name__)
        return RedirectResponse(callback_url + "failed", status_code=303)

    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(seconds=expires_in)).isoformat()
    encrypted_token = _fernet().encrypt(access_token.encode("utf-8")).decode("ascii")
    db.execute(
        """INSERT INTO linkedin_connections
           (user_id, encrypted_token, person_urn, member_name, expires_at, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               encrypted_token = excluded.encrypted_token,
               person_urn = excluded.person_urn,
               member_name = excluded.member_name,
               expires_at = excluded.expires_at,
               updated_at = excluded.updated_at""",
        (
            state_row["user_id"], encrypted_token, f"urn:li:person:{person_id}",
            member_name, expires_at, now.isoformat(), now.isoformat(),
        ),
    )
    db.execute(
        "INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at) "
        "VALUES (?, ?, 'linkedin_connected', 'LinkedIn account connected via OAuth', ?, ?)",
        (str(uuid4()), state_row["user_id"], json.dumps({"expires_at": expires_at}), now.isoformat()),
    )
    return RedirectResponse(callback_url + "connected", status_code=303)


@router.delete("/connection", response_model=ApiResponse[dict])
def disconnect_linkedin():
    db.execute("DELETE FROM linkedin_connections WHERE user_id = ?", (DEFAULT_USER_ID,))
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        "INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at) "
        "VALUES (?, ?, 'linkedin_disconnected', 'LinkedIn account disconnected', '{}', ?)",
        (str(uuid4()), DEFAULT_USER_ID, now),
    )
    return ApiResponse(success=True, data={"connected": False})


def _upload_linkedin_image(access_token: str, owner: str, media: dict) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Linkedin-Version": settings.LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    try:
        initialized = httpx.post(
            "https://api.linkedin.com/rest/images?action=initializeUpload",
            headers=headers,
            json={"initializeUploadRequest": {"owner": owner}},
            timeout=20.0,
        )
        if initialized.status_code not in (200, 201):
            raise _linkedin_http_error(initialized)
        upload_data = initialized.json()["value"]
        upload_url = upload_data["uploadUrl"]
        image_urn = upload_data["image"]
        parsed_url = urlsplit(upload_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname not in ("www.linkedin.com", "linkedin.com")
            or parsed_url.port not in (None, 443)
            or parsed_url.username is not None
            or parsed_url.password is not None
        ):
            logger.error("LinkedIn returned an unexpected image upload URL host")
            raise HTTPException(status_code=502, detail="LinkedIn returned an invalid image upload URL")
        uploaded = httpx.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": media["content_type"],
            },
            content=media["content"],
            timeout=60.0,
        )
        if uploaded.status_code not in (200, 201):
            raise _linkedin_http_error(uploaded)
    except HTTPException:
        raise
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        logger.warning("LinkedIn image upload failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="LinkedIn image upload failed") from exc
    return image_urn


def publish_linkedin_post(post_text: str, media: list[dict] | None = None) -> str:
    row = _connection()
    if not row or row["expires_at"] <= datetime.now(timezone.utc).isoformat():
        raise HTTPException(status_code=409, detail="LinkedIn is not connected or its access token expired")
    access_token = _connection_token(row)
    content = None
    if media:
        if len(media) != 1:
            raise HTTPException(status_code=422, detail="LinkedIn posts currently support one attached image")
        image_urn = _upload_linkedin_image(access_token, row["person_urn"], media[0])
        content = {
            "media": {
                "title": media[0]["filename"],
                "id": image_urn,
            }
        }
    payload = {
        "author": row["person_urn"],
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if content:
        payload["content"] = content
    try:
        response = httpx.post(
            "https://api.linkedin.com/rest/posts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Linkedin-Version": settings.LINKEDIN_API_VERSION,
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json=payload,
            timeout=20.0,
        )
    except httpx.HTTPError as exc:
        logger.warning("LinkedIn publishing request failed: %s", type(exc).__name__)
        raise HTTPException(status_code=502, detail="Could not reach LinkedIn; the post was not retried") from exc
    if response.status_code != 201:
        raise _linkedin_http_error(response)
    post_id = response.headers.get("x-restli-id")
    if not post_id:
        logger.error("LinkedIn created a post but did not return x-restli-id")
        raise HTTPException(
            status_code=502,
            detail="LinkedIn may have accepted the post but returned no post ID; check your LinkedIn feed before retrying",
        )
    return post_id
