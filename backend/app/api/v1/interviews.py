import json
import re
from datetime import date, datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.models.schemas import (
    ApiResponse,
    InterviewMessageRead,
    InterviewSessionRead,
    InterviewStartRequest,
    InterviewTurnRequest,
    InterviewTurnResult,
)

router = APIRouter(prefix="/interviews", tags=["AI Interviewer"])

OPENING_QUESTION = (
    "What did you work on, learn, solve, or notice today? Small progress—or no major progress—is fine."
)
NO_PROGRESS_PATTERN = re.compile(
    r"^(nothing(?: much| significant)?(?: happened)?|no progress|"
    r"not much(?: happened)?|day off|took the day off)(?: today)?[.! ]*$",
    re.IGNORECASE,
)


def _session_data(interview_id: str) -> InterviewSessionRead:
    row = db.fetch_one(
        "SELECT * FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, DEFAULT_USER_ID),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Interview not found")
    messages = db.fetch_all(
        "SELECT id, sender, content, created_at FROM interview_messages "
        "WHERE interview_id = ? ORDER BY created_at, id",
        (interview_id,),
    )
    return InterviewSessionRead(
        id=row["id"],
        interview_date=row["interview_date"],
        mode=row["mode"],
        completed=bool(row["completed"]),
        summary=row["summary"],
        messages=[InterviewMessageRead(**message) for message in messages],
    )


def _store_message(interview_id: str, sender: str, content: str) -> None:
    db.execute(
        """INSERT INTO interview_messages (id, interview_id, sender, content, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (str(uuid4()), interview_id, sender, content, datetime.now(timezone.utc).isoformat()),
    )


def _content_opportunity(text: str) -> str:
    normalized = text.casefold()
    if NO_PROGRESS_PATTERN.search(normalized):
        return "none"
    if re.search(r"\b(opinion|believe|think|trade-?off|agree|disagree)\b", normalized):
        return "technical_opinion"
    if re.search(r"\b(learn|learned|understand|understood|study|studied|discover|discovered)\b", normalized):
        return "learning_experience"
    if re.search(r"\b(build|built|implement|implemented|project|feature|ship|shipped|release)\b", normalized):
        return "project_update"
    if re.search(r"\b(solve|solved|fix|fixed|bug|debug|problem|challenge|concept|explain)\b", normalized):
        return "technical_educational_post"
    return "none"


def _follow_up(answer: str, user_turns: int) -> str:
    normalized = answer.casefold()
    if len(answer.split()) < 10:
        return "Could you add one concrete detail about what you did or noticed?"
    if re.search(r"\b(bug|error|problem|challenge|stuck|issue|failed)\b", normalized):
        return "How did you investigate or resolve it, and what did you learn from the process?"
    if re.search(r"\b(learn|learned|understand|understood|study|studied|discover|discovered)\b", normalized):
        return "What helped the idea click, and where might you apply that understanding next?"
    if re.search(r"\b(build|built|implement|implemented|project|feature|ship|shipped)\b", normalized):
        return "What was the most important design choice or outcome, and how did you verify it?"
    if user_turns == 1:
        return "What was the most interesting part, and why did it matter to you?"
    return "What is one useful takeaway you would want another developer to know?"


def _finish_interview(interview_id: str, summary: str) -> None:
    db.execute(
        """UPDATE interviews SET completed = 1, summary = ?, extracted_topics = ?, updated_at = ?
           WHERE id = ? AND user_id = ?""",
        (
            summary,
            json.dumps([]),
            datetime.now(timezone.utc).isoformat(),
            interview_id,
            DEFAULT_USER_ID,
        ),
    )
    interview = db.fetch_one(
        "SELECT interview_date FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, DEFAULT_USER_ID),
    )
    if summary.strip() and interview:
        db.index_knowledge(
            DEFAULT_USER_ID, "interviews", interview_id,
            f"Interview {interview['interview_date']}", summary,
        )
    else:
        db.remove_knowledge(DEFAULT_USER_ID, "interviews", interview_id)


@router.post("/start", response_model=ApiResponse[InterviewSessionRead])
def start_interview(payload: InterviewStartRequest):
    interview_date = date.today().isoformat()
    existing = db.fetch_one(
        "SELECT id FROM interviews WHERE user_id = ? AND interview_date = ? ORDER BY created_at DESC LIMIT 1",
        (DEFAULT_USER_ID, interview_date),
    )
    if existing:
        return ApiResponse(success=True, data=_session_data(existing["id"]))

    interview_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        """INSERT INTO interviews
           (id, user_id, interview_date, mode, completed, extracted_topics, created_at, updated_at)
           VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
        (interview_id, DEFAULT_USER_ID, interview_date, payload.mode, json.dumps([]), now, now),
    )
    _store_message(interview_id, "ai", OPENING_QUESTION)
    return ApiResponse(success=True, data=_session_data(interview_id))


@router.get("/today", response_model=ApiResponse[Optional[InterviewSessionRead]])
def get_today_interview():
    existing = db.fetch_one(
        "SELECT id FROM interviews WHERE user_id = ? AND interview_date = ? ORDER BY created_at DESC LIMIT 1",
        (DEFAULT_USER_ID, date.today().isoformat()),
    )
    return ApiResponse(
        success=True,
        data=_session_data(existing["id"]) if existing else None,
    )


@router.get("/{interview_id}", response_model=ApiResponse[InterviewSessionRead])
def get_interview(interview_id: str):
    return ApiResponse(success=True, data=_session_data(interview_id))


@router.post("/{interview_id}/turn", response_model=ApiResponse[InterviewTurnResult])
def submit_interview_turn(interview_id: str, payload: InterviewTurnRequest):
    session = db.fetch_one(
        "SELECT id, completed FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, DEFAULT_USER_ID),
    )
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session["completed"]:
        raise HTTPException(status_code=409, detail="This interview is already complete")

    answer = payload.user_response.strip()
    if not answer:
        raise HTTPException(status_code=422, detail="Answer cannot be blank")

    last_message = db.fetch_one(
        "SELECT sender FROM interview_messages WHERE interview_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
        (interview_id,),
    )
    if not last_message or last_message["sender"] != "ai":
        raise HTTPException(status_code=409, detail="The previous answer is still being processed")

    _store_message(interview_id, "user", answer)
    user_messages = db.fetch_all(
        "SELECT content FROM interview_messages WHERE interview_id = ? AND sender = 'user' ORDER BY created_at, id",
        (interview_id,),
    )
    all_answers = [message["content"] for message in user_messages]
    combined = "\n".join(all_answers)
    opportunity = _content_opportunity(combined)
    finish = opportunity == "none" or len(all_answers) >= 3

    if finish:
        summary = "\n".join(all_answers)
        _finish_interview(interview_id, summary)
    else:
        _store_message(interview_id, "ai", _follow_up(answer, len(all_answers)))

    return ApiResponse(
        success=True,
        data=InterviewTurnResult(
            session=_session_data(interview_id),
            content_opportunity=opportunity,
        ),
    )


@router.post("/{interview_id}/complete", response_model=ApiResponse[InterviewSessionRead])
def complete_interview(interview_id: str):
    session = db.fetch_one(
        "SELECT id, completed FROM interviews WHERE id = ? AND user_id = ?",
        (interview_id, DEFAULT_USER_ID),
    )
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if not session["completed"]:
        answers = db.fetch_all(
            "SELECT content FROM interview_messages WHERE interview_id = ? AND sender = 'user' ORDER BY created_at, id",
            (interview_id,),
        )
        _finish_interview(interview_id, "\n".join(answer["content"] for answer in answers))
    return ApiResponse(success=True, data=_session_data(interview_id))
