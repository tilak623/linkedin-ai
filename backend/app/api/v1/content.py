import asyncio
import hmac
import json
import logging
from datetime import date, datetime, time, timedelta, timezone
import sqlite3
from typing import Any
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Header, HTTPException, status
import psycopg

from backend.app.core.config import settings
from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.models.schemas import (
    ApiResponse,
    ContentApprovalRequest,
    ContentPostRead,
    ContentPostUpdate,
    ContentScheduleRead,
)
from backend.app.api.v1.linkedin import publish_linkedin_post

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content", tags=["Content Studio"])


def _read_post(row: dict[str, Any]) -> ContentPostRead:
    approval_log = json.loads(row["approval_log"] or "{}")
    return ContentPostRead(
        id=row["id"],
        title=row["title"],
        topic=row["topic"],
        content_category=row["content_category"],
        final_content=row["final_content"],
        hashtags=json.loads(row["hashtags"] or "[]"),
        status=row["status"],
        scheduled_for=row["scheduled_for"],
        published_at=row["published_at"],
        linkedin_post_id=row["linkedin_post_id"],
        created_at=row["created_at"],
        approved_at=approval_log.get("approved_at"),
    )


@router.get("/schedule", response_model=ApiResponse[ContentScheduleRead])
def get_schedule():
    return ApiResponse(
        success=True,
        data=ContentScheduleRead(
            daily_post_time=settings.DAILY_POST_TIME,
            timezone=settings.DAILY_POST_TIMEZONE,
        ),
    )


@router.post("/scheduler/tick", response_model=ApiResponse[dict[str, bool]])
def trigger_scheduler_tick(authorization: str | None = Header(default=None)):
    expected_token = settings.SCHEDULER_TRIGGER_TOKEN
    if not expected_token:
        raise HTTPException(status_code=503, detail="External scheduler is not configured")
    if not authorization or not hmac.compare_digest(authorization, f"Bearer {expected_token}"):
        raise HTTPException(status_code=401, detail="Invalid scheduler authorization")
    run_scheduler_tick()
    return ApiResponse(success=True, data={"triggered": True})


def _source_evidence(conn) -> dict[str, str] | None:
    interview = conn.execute(
        """SELECT id, interview_date, summary FROM interviews
           WHERE user_id = ? AND completed = 1 AND summary IS NOT NULL AND trim(summary) != ''
             AND NOT EXISTS (
                 SELECT 1 FROM content_posts p
                 WHERE p.user_id = interviews.user_id AND p.topic = 'interview:' || interviews.id
             )
           ORDER BY interview_date DESC, created_at DESC LIMIT 1""",
        (DEFAULT_USER_ID,),
    ).fetchone()
    if interview:
        return {
            "id": interview["id"],
            "title": f"Engineering reflection — {interview['interview_date']}",
            "category": "learning_experience",
            "evidence": interview["summary"].strip(),
            "topic": "interview",
        }

    milestone = conn.execute(
        """SELECT id, title, description, category, lessons_learned
           FROM learning_milestones
           WHERE user_id = ?
             AND NOT EXISTS (
                 SELECT 1 FROM content_posts p
                 WHERE p.user_id = learning_milestones.user_id AND p.topic = 'milestone:' || learning_milestones.id
             )
           ORDER BY milestone_date DESC, created_at DESC LIMIT 1""",
        (DEFAULT_USER_ID,),
    ).fetchone()
    if milestone:
        evidence = milestone["lessons_learned"] or milestone["description"]
        if evidence and evidence.strip():
            return {
                "id": milestone["id"],
                "title": milestone["title"],
                "category": "learning_experience",
                "evidence": evidence.strip(),
                "topic": "milestone",
            }

    project = conn.execute(
        """SELECT id, title, description, maturity, tech_stack, key_achievements
           FROM projects WHERE user_id = ? AND maturity != 'planned'
             AND NOT EXISTS (
                 SELECT 1 FROM content_posts p
                 WHERE p.user_id = projects.user_id AND p.topic = 'project:' || projects.id
             )
           ORDER BY updated_at DESC, created_at DESC LIMIT 1""",
        (DEFAULT_USER_ID,),
    ).fetchone()
    if project:
        details = []
        if project["description"] and project["description"].strip():
            details.append(project["description"].strip())
        achievements = json.loads(project["key_achievements"] or "[]")
        details.extend(item.strip() for item in achievements if isinstance(item, str) and item.strip())
        technologies = json.loads(project["tech_stack"] or "[]")
        if technologies:
            details.append("Technologies: " + ", ".join(technologies))
        if details:
            return {
                "id": project["id"],
                "title": project["title"],
                "category": "project_update",
                "evidence": "\n".join(details),
                "topic": "project",
            }
    return None


def _draft_text(source: dict[str, str]) -> str:
    if source["topic"] == "project":
        opening = f"Project update: {source['title']}."
    else:
        opening = f"A learning note: {source['title']}."
    return f"{opening}\n\n{source['evidence']}\n\n#SoftwareEngineering #LearningInPublic"


def _insert_draft(conn, source: dict[str, str], now: str) -> str:
    post_id = str(uuid4())
    content = _draft_text(source)
    if len(content) > 3000:
        raise HTTPException(
            status_code=422,
            detail="The saved evidence is too long for a LinkedIn post. Shorten it before generating a draft.",
        )
    conn.execute(
        """INSERT INTO content_posts
           (id, user_id, title, topic, content_category, draft_versions, final_content,
            hashtags, status, approval_log, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', '{}', ?, ?)""",
        (
            post_id, DEFAULT_USER_ID, source["title"], f"{source['topic']}:{source['id']}",
            source["category"], json.dumps([content]), content,
            json.dumps(["#SoftwareEngineering", "#LearningInPublic"]), now, now,
        ),
    )
    return post_id


@router.get("/posts", response_model=ApiResponse[list[ContentPostRead]])
def list_posts():
    rows = db.fetch_all(
        "SELECT * FROM content_posts WHERE user_id = ? ORDER BY created_at DESC",
        (DEFAULT_USER_ID,),
    )
    return ApiResponse(success=True, data=[_read_post(row) for row in rows])


@router.post("/generate", response_model=ApiResponse[ContentPostRead], status_code=status.HTTP_201_CREATED)
def generate_draft():
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        source = _source_evidence(conn)
        if not source:
            raise HTTPException(
                status_code=409,
                detail="Add new interview, project, or learning evidence; previously used evidence is not drafted again.",
            )
        post_id = _insert_draft(conn, source, now)
        conn.commit()
        row = conn.execute("SELECT * FROM content_posts WHERE id = ?", (post_id,)).fetchone()
    return ApiResponse(success=True, data=_read_post(dict(row)))


@router.patch("/posts/{post_id}", response_model=ApiResponse[ContentPostRead])
def update_draft(post_id: str, payload: ContentPostUpdate):
    title = payload.title.strip()
    content = payload.final_content.strip()
    if not title or not content:
        raise HTTPException(status_code=422, detail="Title and content cannot be blank")
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM content_posts WHERE id = ? AND user_id = ?",
            (post_id, DEFAULT_USER_ID),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        if row["status"] != "draft":
            raise HTTPException(status_code=409, detail="Only unapproved drafts can be edited")
        versions = json.loads(row["draft_versions"] or "[]")
        versions.append(row["final_content"])
        updated_count = conn.execute(
            """UPDATE content_posts SET title = ?, final_content = ?, draft_versions = ?, updated_at = ?
               WHERE id = ? AND user_id = ? AND status = 'draft'""",
            (title, content, json.dumps(versions), now, post_id, DEFAULT_USER_ID),
        ).rowcount
        if updated_count != 1:
            raise HTTPException(status_code=409, detail="This draft is no longer editable")
        conn.commit()
        updated = conn.execute("SELECT * FROM content_posts WHERE id = ?", (post_id,)).fetchone()
    return ApiResponse(success=True, data=_read_post(dict(updated)))


def _next_publish_time(now: datetime | None = None) -> datetime:
    try:
        zone = ZoneInfo(settings.DAILY_POST_TIMEZONE)
        schedule_time = time.fromisoformat(settings.DAILY_POST_TIME)
        if schedule_time.tzinfo is not None:
            raise ValueError("DAILY_POST_TIME must not include a timezone offset")
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise HTTPException(status_code=503, detail="Daily publishing time or timezone is invalid") from exc
    local_now = (now or datetime.now(timezone.utc)).astimezone(zone)
    scheduled = datetime.combine(local_now.date(), schedule_time, tzinfo=zone)
    if scheduled <= local_now:
        scheduled += timedelta(days=1)
    return scheduled.astimezone(timezone.utc)


@router.post("/posts/{post_id}/approve", response_model=ApiResponse[ContentPostRead])
def approve_and_schedule(post_id: str, payload: ContentApprovalRequest):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Explicit confirmation is required to schedule public posting")
    from backend.app.api.v1.linkedin import get_linkedin_status

    connection_status = get_linkedin_status().data
    if not connection_status or not connection_status.connected:
        raise HTTPException(status_code=409, detail="Connect a valid LinkedIn account before scheduling")
    scheduled_for = _next_publish_time().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM content_posts WHERE id = ? AND user_id = ?",
            (post_id, DEFAULT_USER_ID),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        if row["status"] != "draft":
            raise HTTPException(status_code=409, detail="Only an unapproved draft can be approved")
        approval_log = {
            "approved": True,
            "approved_at": now,
            "scheduled_for": scheduled_for,
            "channel": "linkedin",
        }
        updated_count = conn.execute(
            """UPDATE content_posts
               SET status = 'scheduled', scheduled_for = ?, approval_log = ?, updated_at = ?
               WHERE id = ? AND user_id = ? AND status = 'draft'""",
            (scheduled_for, json.dumps(approval_log), now, post_id, DEFAULT_USER_ID),
        )
        if updated_count.rowcount != 1:
            raise HTTPException(status_code=409, detail="This draft has already changed")
        conn.execute(
            """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
               VALUES (?, ?, 'linkedin_post_approved', 'User approved a LinkedIn post for scheduled publishing', ?, ?)""",
            (str(uuid4()), DEFAULT_USER_ID, json.dumps({"post_id": post_id, "scheduled_for": scheduled_for}), now),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM content_posts WHERE id = ?", (post_id,)).fetchone()
    return ApiResponse(success=True, data=_read_post(dict(updated)))


@router.post("/posts/{post_id}/reschedule", response_model=ApiResponse[ContentPostRead])
def reschedule_missed_post(post_id: str, payload: ContentApprovalRequest):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Explicit confirmation is required to reschedule public posting")
    from backend.app.api.v1.linkedin import get_linkedin_status

    connection_status = get_linkedin_status().data
    if not connection_status or not connection_status.connected:
        raise HTTPException(status_code=409, detail="Connect a valid LinkedIn account before scheduling")
    scheduled_for = _next_publish_time().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM content_posts WHERE id = ? AND user_id = ?",
            (post_id, DEFAULT_USER_ID),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        if row["status"] != "missed_schedule":
            raise HTTPException(status_code=409, detail="Only a post held for a missed schedule can be re-approved")
        previous_log = json.loads(row["approval_log"] or "{}")
        approval_history = previous_log.get("previous_approvals", [])
        approval_history.append(previous_log)
        approval_log = {
            "approved": True,
            "approved_at": now,
            "scheduled_for": scheduled_for,
            "channel": "linkedin",
            "previous_approvals": approval_history,
        }
        updated_count = conn.execute(
            """UPDATE content_posts
               SET status = 'scheduled', scheduled_for = ?, approval_log = ?, updated_at = ?
               WHERE id = ? AND user_id = ? AND status = 'missed_schedule'""",
            (scheduled_for, json.dumps(approval_log), now, post_id, DEFAULT_USER_ID),
        )
        if updated_count.rowcount != 1:
            raise HTTPException(status_code=409, detail="This post has already changed")
        conn.execute(
            """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
               VALUES (?, ?, 'linkedin_post_reapproved', 'User re-approved a missed LinkedIn post for scheduled publishing', ?, ?)""",
            (str(uuid4()), DEFAULT_USER_ID, json.dumps({"post_id": post_id, "scheduled_for": scheduled_for}), now),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM content_posts WHERE id = ?", (post_id,)).fetchone()
    return ApiResponse(success=True, data=_read_post(dict(updated)))


def _create_daily_draft(run_date: date) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        exists = conn.execute(
            "SELECT run_date FROM daily_post_runs WHERE run_date = ?",
            (run_date.isoformat(),),
        ).fetchone()
        if exists:
            return
        source = _source_evidence(conn)
        if not source:
            return
        post_id = _insert_draft(conn, source, now)
        conn.execute(
            "INSERT INTO daily_post_runs (run_date, post_id, status, created_at) VALUES (?, ?, 'drafted', ?)",
            (run_date.isoformat(), post_id, now),
        )
        conn.commit()


def _claim_due_posts(now: datetime) -> list[dict[str, Any]]:
    claimed = []
    now_text = now.astimezone(timezone.utc).isoformat()
    with db.get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute(
            """SELECT id, final_content, scheduled_for FROM content_posts
               WHERE user_id = ? AND status = 'scheduled' AND scheduled_for <= ?
               ORDER BY scheduled_for, created_at""",
            (DEFAULT_USER_ID, now_text),
        ).fetchall()
        for row in rows:
            scheduled_at = datetime.fromisoformat(row["scheduled_for"])
            if now.astimezone(timezone.utc) - scheduled_at > timedelta(minutes=15):
                conn.execute(
                    """UPDATE content_posts SET status = 'missed_schedule', updated_at = ?
                       WHERE id = ? AND user_id = ? AND status = 'scheduled'""",
                    (now_text, row["id"], DEFAULT_USER_ID),
                )
                conn.execute(
                    """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
                       VALUES (?, ?, 'linkedin_schedule_missed', 'Scheduled post was held for review because the server was offline', ?, ?)""",
                    (
                        str(uuid4()), DEFAULT_USER_ID,
                        json.dumps({"post_id": row["id"], "scheduled_for": row["scheduled_for"]}),
                        now_text,
                    ),
                )
                continue
            result = conn.execute(
                """UPDATE content_posts SET status = 'publishing', updated_at = ?
                   WHERE id = ? AND user_id = ? AND status = 'scheduled'""",
                (now_text, row["id"], DEFAULT_USER_ID),
            )
            if result.rowcount == 1:
                claimed.append(dict(row))
        conn.commit()
    return claimed


def recover_interrupted_posts() -> None:
    now = datetime.now(timezone.utc).isoformat()
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id FROM content_posts WHERE user_id = ? AND status = 'publishing'",
            (DEFAULT_USER_ID,),
        ).fetchall()
        for row in rows:
            conn.execute(
                "UPDATE content_posts SET status = 'publish_failed', updated_at = ? WHERE id = ? AND status = 'publishing'",
                (now, row["id"]),
            )
            conn.execute(
                """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
                   VALUES (?, ?, 'linkedin_publish_interrupted', 'Publishing was interrupted; verify the LinkedIn feed before taking action', ?, ?)""",
                (str(uuid4()), DEFAULT_USER_ID, json.dumps({"post_id": row["id"]}), now),
            )
        conn.commit()


def _publish_claimed_post(post: dict[str, Any], now: datetime) -> None:
    try:
        linkedin_post_id = publish_linkedin_post(post["final_content"])
    except HTTPException as exc:
        logger.warning("Scheduled LinkedIn post %s failed (%s)", post["id"], exc.status_code)
        db.execute(
            "UPDATE content_posts SET status = 'publish_failed', updated_at = ? WHERE id = ? AND status = 'publishing'",
            (now.astimezone(timezone.utc).isoformat(), post["id"]),
        )
        db.execute(
            """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
               VALUES (?, ?, 'linkedin_publish_failed', 'Scheduled LinkedIn publishing failed; automatic retry was prevented', ?, ?)""",
            (
                str(uuid4()), DEFAULT_USER_ID,
                json.dumps({"post_id": post["id"], "http_status": exc.status_code}),
                now.astimezone(timezone.utc).isoformat(),
            ),
        )
        return
    published_at = now.astimezone(timezone.utc).isoformat()
    db.execute(
        """UPDATE content_posts
           SET status = 'published', published_at = ?, linkedin_post_id = ?, updated_at = ?
           WHERE id = ? AND status = 'publishing'""",
        (published_at, linkedin_post_id, published_at, post["id"]),
    )
    db.execute(
        """INSERT INTO audit_logs (id, user_id, action_type, description, metadata, created_at)
           VALUES (?, ?, 'linkedin_post_published', 'Approved LinkedIn post published by the scheduled publisher', ?, ?)""",
        (str(uuid4()), DEFAULT_USER_ID, json.dumps({"post_id": post["id"], "linkedin_post_id": linkedin_post_id}), published_at),
    )


def run_scheduler_tick(now: datetime | None = None) -> None:
    current = now or datetime.now(timezone.utc)
    try:
        zone = ZoneInfo(settings.DAILY_POST_TIMEZONE)
        schedule_time = time.fromisoformat(settings.DAILY_POST_TIME)
        if schedule_time.tzinfo is not None:
            raise ValueError("DAILY_POST_TIME must not include a timezone offset")
    except (ValueError, ZoneInfoNotFoundError) as exc:
        logger.error("Daily LinkedIn scheduler configuration is invalid: %s", exc)
        return
    local_now = current.astimezone(zone)
    if local_now.timetz().replace(tzinfo=None, second=0, microsecond=0) >= schedule_time:
        _create_daily_draft(local_now.date())
    for post in _claim_due_posts(current):
        _publish_claimed_post(post, current)


async def scheduler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(run_scheduler_tick)
        except (sqlite3.Error, psycopg.Error):
            logger.exception("LinkedIn scheduler database operation failed")
        await asyncio.sleep(30)
