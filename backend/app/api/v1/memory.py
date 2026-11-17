import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.core.db import DEFAULT_USER_ID, db
from backend.app.models.schemas import (
    ApiResponse,
    KnowledgeSearchResult,
    MilestoneCreate,
    MilestoneRead,
    MilestoneUpdate,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    SkillCreate,
    SkillRead,
    SkillUpdate,
)

router = APIRouter(prefix="/memory", tags=["Professional Memory"])


def _clean_required(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail=f"{label} cannot be blank")
    return cleaned


def _check_duplicate(table: str, column: str, value: str, exclude_id: Optional[str] = None) -> None:
    query = (
        f"SELECT id FROM {table} "
        f"WHERE user_id = ? AND lower(trim({column})) = lower(trim(?))"
    )
    params: tuple = (DEFAULT_USER_ID, value)
    if exclude_id:
        query += " AND id != ?"
        params += (exclude_id,)
    if db.fetch_one(query, params):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A {table[:-1]} with this name already exists",
        )


def _skill_read(row: Dict[str, Any]) -> SkillRead:
    row["verified_by_project"] = bool(row["verified_by_project"])
    return SkillRead(**row)


def _project_read(row: Dict[str, Any]) -> ProjectRead:
    for field in ("tech_stack", "key_achievements", "screenshots"):
        if isinstance(row[field], str):
            row[field] = json.loads(row[field] or "[]")
    return ProjectRead(**row)


def _milestone_read(row: Dict[str, Any]) -> MilestoneRead:
    return MilestoneRead(**row)


def _skill_index_content(skill: Dict[str, Any]) -> str:
    return " ".join(
        str(skill.get(field) or "")
        for field in ("proficiency_level", "category", "evidence_notes")
    )


def _project_index_content(project: Dict[str, Any]) -> str:
    return " ".join(
        [
            str(project.get("description") or ""),
            str(project.get("maturity") or ""),
            str(project.get("repo_name") or ""),
            " ".join(project.get("tech_stack") or []),
            " ".join(project.get("key_achievements") or []),
        ]
    )


def _milestone_index_content(milestone: Dict[str, Any]) -> str:
    return " ".join(
        str(milestone.get(field) or "")
        for field in ("description", "category", "lessons_learned")
    )


@router.get("/skills", response_model=ApiResponse[List[SkillRead]])
def list_skills():
    rows = db.fetch_all(
        "SELECT * FROM skills WHERE user_id = ? ORDER BY created_at DESC",
        (DEFAULT_USER_ID,),
    )
    return ApiResponse(success=True, data=[_skill_read(row) for row in rows])


@router.post("/skills", response_model=ApiResponse[SkillRead], status_code=201)
def create_skill(payload: SkillCreate):
    name = _clean_required(payload.name, "Skill name")
    _check_duplicate("skills", "name", name)
    skill_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    skill = payload.model_dump()
    skill.update({"id": skill_id, "user_id": DEFAULT_USER_ID, "name": name, "created_at": now, "updated_at": now})
    db.execute(
        """INSERT INTO skills
           (id, user_id, name, category, proficiency_level, verified_by_project, evidence_notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            skill_id, DEFAULT_USER_ID, name, skill["category"], skill["proficiency_level"],
            int(skill["verified_by_project"]), skill["evidence_notes"], now, now,
        ),
    )
    db.index_knowledge(DEFAULT_USER_ID, "skills", skill_id, name, _skill_index_content(skill))
    return ApiResponse(success=True, data=_skill_read(skill))


@router.patch("/skills/{skill_id}", response_model=ApiResponse[SkillRead])
def update_skill(skill_id: str, payload: SkillUpdate):
    row = db.fetch_one("SELECT * FROM skills WHERE id = ? AND user_id = ?", (skill_id, DEFAULT_USER_ID))
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    if "name" in changes:
        changes["name"] = _clean_required(changes["name"] or "", "Skill name")
        _check_duplicate("skills", "name", changes["name"], skill_id)
    if "proficiency_level" in changes and changes["proficiency_level"] is None:
        raise HTTPException(status_code=422, detail="Proficiency level cannot be null")

    updated = {**row, **changes, "updated_at": datetime.now(timezone.utc).isoformat()}
    db.execute(
        """UPDATE skills SET name = ?, category = ?, proficiency_level = ?, verified_by_project = ?,
           evidence_notes = ?, updated_at = ? WHERE id = ? AND user_id = ?""",
        (
            updated["name"], updated["category"], updated["proficiency_level"],
            int(bool(updated["verified_by_project"])), updated["evidence_notes"],
            updated["updated_at"], skill_id, DEFAULT_USER_ID,
        ),
    )
    updated["verified_by_project"] = bool(updated["verified_by_project"])
    db.index_knowledge(DEFAULT_USER_ID, "skills", skill_id, updated["name"], _skill_index_content(updated))
    return ApiResponse(success=True, data=_skill_read(updated))


@router.delete("/skills/{skill_id}", response_model=ApiResponse[dict])
def delete_skill(skill_id: str):
    row = db.fetch_one("SELECT id FROM skills WHERE id = ? AND user_id = ?", (skill_id, DEFAULT_USER_ID))
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.execute("DELETE FROM skills WHERE id = ? AND user_id = ?", (skill_id, DEFAULT_USER_ID))
    db.remove_knowledge(DEFAULT_USER_ID, "skills", skill_id)
    return ApiResponse(success=True, data={"deleted": True})


@router.get("/projects", response_model=ApiResponse[List[ProjectRead]])
def list_projects():
    rows = db.fetch_all(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC",
        (DEFAULT_USER_ID,),
    )
    return ApiResponse(success=True, data=[_project_read(row) for row in rows])


@router.post("/projects", response_model=ApiResponse[ProjectRead], status_code=201)
def create_project(payload: ProjectCreate):
    project = payload.model_dump()
    project["title"] = _clean_required(project["title"], "Project title")
    _check_duplicate("projects", "title", project["title"])
    project_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    project.update({"id": project_id, "user_id": DEFAULT_USER_ID, "created_at": now, "updated_at": now})
    db.execute(
        """INSERT INTO projects
           (id, user_id, title, description, maturity, github_url, repo_name, tech_stack,
            key_achievements, screenshots, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            project_id, DEFAULT_USER_ID, project["title"], project["description"], project["maturity"],
            project["github_url"], project["repo_name"], json.dumps(project["tech_stack"]),
            json.dumps(project["key_achievements"]), json.dumps(project["screenshots"]), now, now,
        ),
    )
    db.index_knowledge(DEFAULT_USER_ID, "projects", project_id, project["title"], _project_index_content(project))
    return ApiResponse(success=True, data=_project_read(project))


@router.patch("/projects/{project_id}", response_model=ApiResponse[ProjectRead])
def update_project(project_id: str, payload: ProjectUpdate):
    row = db.fetch_one("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, DEFAULT_USER_ID))
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    for field in ("tech_stack", "key_achievements", "screenshots"):
        row[field] = json.loads(row[field] or "[]")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    if "title" in changes:
        changes["title"] = _clean_required(changes["title"] or "", "Project title")
        _check_duplicate("projects", "title", changes["title"], project_id)
    if "maturity" in changes and changes["maturity"] is None:
        raise HTTPException(status_code=422, detail="Project maturity cannot be null")
    for field in ("tech_stack", "key_achievements", "screenshots"):
        if field in changes and changes[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")
    updated = {**row, **changes, "updated_at": datetime.now(timezone.utc).isoformat()}
    db.execute(
        """UPDATE projects SET title = ?, description = ?, maturity = ?, github_url = ?, repo_name = ?,
           tech_stack = ?, key_achievements = ?, screenshots = ?, updated_at = ?
           WHERE id = ? AND user_id = ?""",
        (
            updated["title"], updated["description"], updated["maturity"], updated["github_url"],
            updated["repo_name"], json.dumps(updated["tech_stack"]),
            json.dumps(updated["key_achievements"]), json.dumps(updated["screenshots"]),
            updated["updated_at"], project_id, DEFAULT_USER_ID,
        ),
    )
    db.index_knowledge(DEFAULT_USER_ID, "projects", project_id, updated["title"], _project_index_content(updated))
    return ApiResponse(success=True, data=_project_read(updated))


@router.delete("/projects/{project_id}", response_model=ApiResponse[dict])
def delete_project(project_id: str):
    row = db.fetch_one("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, DEFAULT_USER_ID))
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    db.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, DEFAULT_USER_ID))
    db.remove_knowledge(DEFAULT_USER_ID, "projects", project_id)
    return ApiResponse(success=True, data={"deleted": True})


@router.get("/milestones", response_model=ApiResponse[List[MilestoneRead]])
def list_milestones():
    rows = db.fetch_all(
        "SELECT * FROM learning_milestones WHERE user_id = ? ORDER BY milestone_date DESC, created_at DESC",
        (DEFAULT_USER_ID,),
    )
    return ApiResponse(success=True, data=[_milestone_read(row) for row in rows])


@router.post("/milestones", response_model=ApiResponse[MilestoneRead], status_code=201)
def create_milestone(payload: MilestoneCreate):
    milestone = payload.model_dump()
    milestone["title"] = _clean_required(milestone["title"], "Milestone title")
    _check_duplicate("learning_milestones", "title", milestone["title"])
    milestone_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    milestone.update({
        "id": milestone_id, "user_id": DEFAULT_USER_ID,
        "milestone_date": milestone["milestone_date"].isoformat(), "created_at": now,
    })
    db.execute(
        """INSERT INTO learning_milestones
           (id, user_id, title, description, category, milestone_date, lessons_learned, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            milestone_id, DEFAULT_USER_ID, milestone["title"], milestone["description"],
            milestone["category"], milestone["milestone_date"], milestone["lessons_learned"], now,
        ),
    )
    db.index_knowledge(
        DEFAULT_USER_ID, "learning_milestones", milestone_id,
        milestone["title"], _milestone_index_content(milestone),
    )
    return ApiResponse(success=True, data=_milestone_read(milestone))


@router.patch("/milestones/{milestone_id}", response_model=ApiResponse[MilestoneRead])
def update_milestone(milestone_id: str, payload: MilestoneUpdate):
    row = db.fetch_one(
        "SELECT * FROM learning_milestones WHERE id = ? AND user_id = ?",
        (milestone_id, DEFAULT_USER_ID),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Learning milestone not found")
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")
    if "title" in changes:
        changes["title"] = _clean_required(changes["title"] or "", "Milestone title")
        _check_duplicate("learning_milestones", "title", changes["title"], milestone_id)
    if "milestone_date" in changes and changes["milestone_date"] is None:
        raise HTTPException(status_code=422, detail="Milestone date cannot be null")
    if "milestone_date" in changes and changes["milestone_date"] is not None:
        changes["milestone_date"] = changes["milestone_date"].isoformat()
    updated = {**row, **changes}
    db.execute(
        """UPDATE learning_milestones SET title = ?, description = ?, category = ?, milestone_date = ?,
           lessons_learned = ? WHERE id = ? AND user_id = ?""",
        (
            updated["title"], updated["description"], updated["category"], updated["milestone_date"],
            updated["lessons_learned"], milestone_id, DEFAULT_USER_ID,
        ),
    )
    db.index_knowledge(
        DEFAULT_USER_ID, "learning_milestones", milestone_id,
        updated["title"], _milestone_index_content(updated),
    )
    return ApiResponse(success=True, data=_milestone_read(updated))


@router.delete("/milestones/{milestone_id}", response_model=ApiResponse[dict])
def delete_milestone(milestone_id: str):
    row = db.fetch_one(
        "SELECT id FROM learning_milestones WHERE id = ? AND user_id = ?",
        (milestone_id, DEFAULT_USER_ID),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Learning milestone not found")
    db.execute(
        "DELETE FROM learning_milestones WHERE id = ? AND user_id = ?",
        (milestone_id, DEFAULT_USER_ID),
    )
    db.remove_knowledge(DEFAULT_USER_ID, "learning_milestones", milestone_id)
    return ApiResponse(success=True, data={"deleted": True})


@router.get("/export", response_model=ApiResponse[dict])
def export_memory():
    user = db.fetch_one(
        "SELECT full_name, email FROM users WHERE id = ?",
        (DEFAULT_USER_ID,),
    )
    profile = db.fetch_one(
        "SELECT * FROM professional_profiles WHERE user_id = ?",
        (DEFAULT_USER_ID,),
    )
    skills = db.fetch_all(
        "SELECT * FROM skills WHERE user_id = ? ORDER BY name COLLATE NOCASE",
        (DEFAULT_USER_ID,),
    )
    projects = db.fetch_all(
        "SELECT * FROM projects WHERE user_id = ? ORDER BY title COLLATE NOCASE",
        (DEFAULT_USER_ID,),
    )
    milestones = db.fetch_all(
        "SELECT * FROM learning_milestones WHERE user_id = ? ORDER BY milestone_date DESC",
        (DEFAULT_USER_ID,),
    )
    return ApiResponse(
        success=True,
        data={
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "profile": profile,
            "skills": [_skill_read(row).model_dump() for row in skills],
            "projects": [_project_read(row).model_dump() for row in projects],
            "milestones": [_milestone_read(row).model_dump() for row in milestones],
        },
    )


@router.get("/search", response_model=ApiResponse[List[KnowledgeSearchResult]])
def search_knowledge(q: str = Query(min_length=1, max_length=200)):
    tokens = re.findall(r"\w+", q, flags=re.UNICODE)
    if not tokens:
        return ApiResponse(success=True, data=[])
    expression = " AND ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens)
    rows = db.fetch_all(
        """SELECT entity_type, entity_id, title,
                  snippet(knowledge_fts, 4, '', '', ' … ', 18) AS snippet
           FROM knowledge_fts
           WHERE knowledge_fts MATCH ? AND user_id = ?
           ORDER BY bm25(knowledge_fts) LIMIT 50""",
        (expression, DEFAULT_USER_ID),
    )
    return ApiResponse(success=True, data=[KnowledgeSearchResult(**row) for row in rows])
