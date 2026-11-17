from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.models.schemas import (
    ApiResponse,
    ProfileOnboardingRequest,
    UserProfileRead,
)

router = APIRouter(prefix="/profile", tags=["Professional Profile"])


@router.get("", response_model=ApiResponse[UserProfileRead])
def get_profile():
    row = db.fetch_one(
        "SELECT * FROM professional_profiles WHERE user_id = ?",
        (DEFAULT_USER_ID,),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Professional profile not found")
    return ApiResponse(success=True, data=UserProfileRead(**row))


@router.post("/onboard", response_model=ApiResponse[UserProfileRead])
def complete_onboarding(payload: ProfileOnboardingRequest):
    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=422, detail="Full name cannot be blank")

    skills = []
    seen_names = set()
    for submitted_skill in payload.initial_skills:
        skill = submitted_skill.model_dump()
        skill["name"] = skill["name"].strip()
        if not skill["name"]:
            raise HTTPException(status_code=422, detail="Skill names cannot be blank")
        normalized_name = skill["name"].casefold()
        if normalized_name in seen_names:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate skill in onboarding: {skill['name']}",
            )
        seen_names.add(normalized_name)
        if db.fetch_one(
            "SELECT id FROM skills WHERE user_id = ? AND lower(trim(name)) = lower(trim(?))",
            (DEFAULT_USER_ID, skill["name"]),
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Skill already exists: {skill['name']}",
            )
        skills.append(skill)

    now = datetime.now(timezone.utc).isoformat()
    profile_id = str(uuid4())
    with db.get_connection() as conn:
        existing_profile = conn.execute(
            "SELECT id FROM professional_profiles WHERE user_id = ?",
            (DEFAULT_USER_ID,),
        ).fetchone()
        if existing_profile:
            profile_id = existing_profile["id"]
            conn.execute(
                """UPDATE professional_profiles
                   SET headline = ?, summary = ?, career_direction = ?, target_audience = ?,
                       writing_voice_notes = ?, seniority_level = ?, updated_at = ?
                   WHERE id = ? AND user_id = ?""",
                (
                    payload.headline, payload.summary, payload.career_direction,
                    payload.target_audience, payload.writing_voice_notes,
                    payload.seniority_level, now, profile_id, DEFAULT_USER_ID,
                ),
            )
        else:
            conn.execute(
                """INSERT INTO professional_profiles
                   (id, user_id, headline, summary, career_direction, target_audience,
                    writing_voice_notes, seniority_level, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    profile_id, DEFAULT_USER_ID, payload.headline, payload.summary,
                    payload.career_direction, payload.target_audience,
                    payload.writing_voice_notes, payload.seniority_level, now, now,
                ),
            )
        conn.execute(
            "UPDATE users SET full_name = ?, onboarding_completed = 1, updated_at = ? WHERE id = ?",
            (full_name, now, DEFAULT_USER_ID),
        )
        for skill in skills:
            skill_id = str(uuid4())
            skill["id"] = skill_id
            skill["user_id"] = DEFAULT_USER_ID
            skill["created_at"] = now
            skill["updated_at"] = now
            conn.execute(
                """INSERT INTO skills
                   (id, user_id, name, category, proficiency_level, verified_by_project,
                    evidence_notes, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    skill_id, DEFAULT_USER_ID, skill["name"], skill["category"],
                    skill["proficiency_level"], int(skill["verified_by_project"]),
                    skill["evidence_notes"], now, now,
                ),
            )
        conn.commit()

    profile = db.fetch_one(
        "SELECT * FROM professional_profiles WHERE id = ? AND user_id = ?",
        (profile_id, DEFAULT_USER_ID),
    )
    profile_content = " ".join(
        str(profile.get(field) or "")
        for field in ("summary", "career_direction", "target_audience", "writing_voice_notes")
    )
    db.index_knowledge(
        DEFAULT_USER_ID, "profile", profile_id,
        profile.get("headline") or "Professional profile", profile_content,
    )
    for skill in skills:
        db.index_knowledge(
            DEFAULT_USER_ID, "skills", skill["id"], skill["name"],
            " ".join(
                str(skill.get(field) or "")
                for field in ("proficiency_level", "category", "evidence_notes")
            ),
        )
    return ApiResponse(success=True, data=UserProfileRead(**profile))
