from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db_queries import get_all_roles
from db_queries import get_role_details
from pydantic import BaseModel
from skill_gap_engine import analyze_role_gap
from db_queries import get_learning_resources
import sqlite3
from db_queries import get_connection
from auth_utils import hash_password, verify_password
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from pydantic import BaseModel, Field, field_validator
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
import json
from fastapi import Depends
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

app = FastAPI(
    title="AI Skill Gap Analyzer",
    description="API for analysing student skills and career requirements",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SKILLBRIDGE_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SKILLBRIDGE_SECRET_KEY environment variable is missing")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def create_access_token(student_id: int):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(student_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

security = HTTPBearer()


def get_current_student(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        student_id = int(payload.get("sub"))

    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    with get_connection() as conn:

        student = conn.execute("""
            SELECT student_id, name, email
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

    if student is None:
        raise HTTPException(
            status_code=401,
            detail="Student not found"
        )

    return student

class SkillAnalysisRequest(BaseModel):

    role_id: int = Field(gt=0)

    student_skills: list[str] = Field(min_length=1)

    @field_validator("student_skills")
    @classmethod
    def validate_skills(cls, skills):

        cleaned_skills = [
            skill.strip()
            for skill in skills
            if skill.strip()
        ]

        if not cleaned_skills:
            raise ValueError("At least one valid skill is required")

        return cleaned_skills
    
class StudentCreate(BaseModel):

    name: str = Field(min_length=2, max_length=100)

    email: str = Field(min_length=5, max_length=150)

    password: str = Field(min_length=8, max_length=128)

    @field_validator("name", "email")
    @classmethod
    def remove_extra_spaces(cls, value):
        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):

        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Enter a valid email address")

        return value
    
class StudentLogin(BaseModel):

    email: str = Field(min_length=5, max_length=150)

    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return value.strip()
    
class ProgressInitialize(BaseModel):

    role_id: int = Field(gt=0)

    student_skills: list[str] = Field(min_length=1)

    @field_validator("student_skills")
    @classmethod
    def validate_skills(cls, skills):

        cleaned = [
            skill.strip()
            for skill in skills
            if skill.strip()
        ]

        if not cleaned:
            raise ValueError("At least one valid skill is required")

        return cleaned

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Skill Gap Analyzer API",
        "status": "Running successfully"
    }

@app.get("/roles")
def read_roles():

    roles = get_all_roles()

    return {
        "total_roles": len(roles),
        "roles": roles
    }

@app.get("/roles/{role_id}")
def read_role_details(role_id: int):

    role = get_role_details(role_id)

    if role is None:
        raise HTTPException(
            status_code=404,
            detail="Job role not found"
        )

    return role

@app.post("/analyze-skills")
def analyze_skills(
    request: SkillAnalysisRequest,
    current_student = Depends(get_current_student)
):

    # Calculate skill gap
    result = analyze_role_gap(
        request.role_id,
        request.student_skills
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job role not found"
        )

    # Save analysis against the logged-in student
    with get_connection() as conn:

        conn.execute("""
            INSERT INTO student_skill_analysis (
                student_id,
                role_id,
                student_skills,
                matched_skills,
                missing_skills,
                match_percentage,
                total_required_skills,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(student_id) DO UPDATE SET
                role_id = excluded.role_id,
                student_skills = excluded.student_skills,
                matched_skills = excluded.matched_skills,
                missing_skills = excluded.missing_skills,
                match_percentage = excluded.match_percentage,
                total_required_skills = excluded.total_required_skills,
                updated_at = CURRENT_TIMESTAMP
        """, (
            current_student["student_id"],
            request.role_id,
            json.dumps(request.student_skills),
            json.dumps(result["matched_skills"]),
            json.dumps(result["missing_skills"]),
            result["match_percentage"],
            result.get(
            "total_required_skills",
            len(result["matched_skills"]) + len(result["missing_skills"])
        )))

    return result

@app.get("/student-analysis")
def get_student_analysis(
    current_student = Depends(get_current_student)
):

    with get_connection() as conn:

        analysis = conn.execute("""
            SELECT
                a.role_id,
                a.student_skills,
                a.matched_skills,
                a.missing_skills,
                a.match_percentage,
                a.total_required_skills,
                r.job_role,
                r.sector
            FROM student_skill_analysis a
            JOIN roles r ON a.role_id = r.role_id
            WHERE a.student_id = ?
        """, (current_student["student_id"],)).fetchone()

    # No previous analysis found
    if analysis is None:
        return {
            "has_analysis": False
        }

    # Return the saved analysis
    return {
        "has_analysis": True,
        "role_id": analysis["role_id"],
        "student_skills": json.loads(analysis["student_skills"]),
        "matched_skills": json.loads(analysis["matched_skills"]),
        "missing_skills": json.loads(analysis["missing_skills"]),
        "match_percentage": analysis["match_percentage"],
        "total_required_skills": analysis["total_required_skills"],
        "job_role": analysis["job_role"],
        "sector": analysis["sector"]
    }

@app.get("/resources/{skill_name}")
def read_learning_resources(skill_name: str):

    skill_name = skill_name.strip()

    if not skill_name:
        raise HTTPException(
            status_code=400,
            detail="Skill name cannot be empty"
        )

    resources = get_learning_resources(skill_name)

    if not resources:
        raise HTTPException(
            status_code=404,
            detail=f"No learning resources found for {skill_name}"
        )

    return {
        "skill": skill_name,
        "total_resources": len(resources),
        "resources": resources
    }
@app.post("/students", status_code=201)
def create_student(student: StudentCreate):

    try:
        password_hash = hash_password(student.password)
        with get_connection() as conn:

            cursor = conn.execute("""
                INSERT INTO students (name, email, password_hash)
                VALUES (?, ?, ?)
            """, (
                student.name,
                student.email,
                password_hash
            ))

            student_id = cursor.lastrowid

        return {
            "message": "Student registered successfully",
            "student_id": student_id,
            "name": student.name,
            "email": student.email
        }

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=409,
            detail="This email is already registered"
        )

@app.post("/login")
def login_student(credentials: StudentLogin):

    with get_connection() as conn:
        student = conn.execute("""
            SELECT student_id, name, email, password_hash
            FROM students
            WHERE email = ?
        """, (credentials.email,)).fetchone()

    # Check whether student exists
    if student is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        credentials.password,
        student["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(student["student_id"])

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "student": {
            "student_id": student["student_id"],
            "name": student["name"],
            "email": student["email"]
        }
    }


def create_access_token(student_id: int):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(student_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
@app.post("/progress/initialize")
def initialize_progress(
    request: ProgressInitialize,
    current_student=Depends(get_current_student)
):

    student_id = current_student["student_id"]

    # Check whether student exists
    with get_connection() as conn:

        student = conn.execute(
            "SELECT student_id FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Analyze student's skills
    result = analyze_role_gap(
        request.role_id,
        request.student_skills
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Job role not found"
        )

    # Initialize matched skills at 100%
    # Initialize missing skills at 0%
    with get_connection() as conn:

        for skill in result["matched_skills"]:

            conn.execute("""
                INSERT INTO student_skill_progress
                (student_id, role_id, skill_name, progress_percentage)
                VALUES (?, ?, ?, 100)
                ON CONFLICT(student_id, role_id, skill_name)
                DO NOTHING
            """, (
                student_id,
                request.role_id,
                skill
            ))

        for skill in result["missing_skills"]:

            conn.execute("""
                INSERT INTO student_skill_progress
                (student_id, role_id, skill_name, progress_percentage)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(student_id, role_id, skill_name)
                DO NOTHING
            """, (
                student_id,
                request.role_id,
                skill
            ))

    return {
        "message": "Learning progress initialized successfully",
        "student_id": student_id,
        "job_role": result["job_role"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "initial_match_percentage": result["match_percentage"]
    }

@app.get("/progress/{role_id}")
def get_student_progress(
    role_id: int,
    current_student=Depends(get_current_student)
):

    student_id = current_student["student_id"]

    with get_connection() as conn:

        # Check whether student exists
        student = conn.execute("""
            SELECT student_id
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        # Retrieve skill progress
        rows = conn.execute("""
            SELECT
                skill_name,
                progress_percentage
            FROM student_skill_progress
            WHERE student_id = ?
            AND role_id = ?
        """, (student_id, role_id)).fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Learning progress not initialized"
        )

    total_skills = len(rows)

    completed_percentage = sum(
        row["progress_percentage"] for row in rows
    )

    overall_progress = completed_percentage / total_skills

    return {
        "student_id": student_id,
        "role_id": role_id,
        "total_skills": total_skills,
        "overall_progress": round(overall_progress, 2),
        "skills": [
            {
                "skill_name": row["skill_name"],
                "progress": row["progress_percentage"]
            }
            for row in rows
        ]
    }
class ProgressUpdate(BaseModel):
    role_id: int = Field(gt=0)
    skill_name: str = Field(min_length=1)
    progress_percentage: float = Field(
        ge=0,
        le=100
    )

    @field_validator("skill_name")
    @classmethod
    def clean_skill_name(cls, value):
        return value.strip()
    
@app.put("/progress/update")
def update_learning_progress(
    request: ProgressUpdate,
    current_student=Depends(get_current_student)
):

    student_id = current_student["student_id"]
    with get_connection() as conn:
        # Check student
        student = conn.execute("""
            SELECT student_id
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        # Check whether skill exists in progress table
        skill = conn.execute("""
            SELECT progress_id
            FROM student_skill_progress
            WHERE student_id = ?
            AND role_id = ?
            AND skill_name = ?""", 
            (
            student_id,
            request.role_id,
            request.skill_name.lower()
        )).fetchone()

        if skill is None:
            raise HTTPException(
                status_code=404,
                detail="Skill not found in student's learning plan"
            )

        # Update progress
        conn.execute("""
            UPDATE student_skill_progress
            SET progress_percentage = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?
            AND role_id = ?
            AND skill_name = ?
        """, (
            request.progress_percentage,
            student_id,
            request.role_id,
            request.skill_name.lower()
        ))

    return {
        "message": "Learning progress updated successfully",
        "student_id": student_id,
        "skill_name": request.skill_name,
        "progress_percentage": request.progress_percentage
    }

@app.get("/dashboard/{role_id}")
def get_student_dashboard(
    role_id: int,
    current_student=Depends(get_current_student)
):
    student_id = current_student["student_id"]
    with get_connection() as conn:

        # Get student information
        student = conn.execute("""
            SELECT student_id, name, email
            FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if student is None:
            raise HTTPException(
                status_code=404,
                detail="Student not found"
            )

        # Get selected job role
        role = conn.execute("""
            SELECT role_id, job_role, sector
            FROM roles
            WHERE role_id = ?
        """, (role_id,)).fetchone()

        if role is None:
            raise HTTPException(
                status_code=404,
                detail="Job role not found"
            )

        # Get all skill progress
        skills = conn.execute("""
            SELECT skill_name, progress_percentage
            FROM student_skill_progress
            WHERE student_id = ?
            AND role_id = ?
            ORDER BY skill_name
        """, (student_id, role_id)).fetchall()

    if not skills:
        raise HTTPException(
            status_code=404,
            detail="Learning progress not initialized"
        )

    # Categorize skills
    completed = []
    in_progress = []
    not_started = []

    for skill in skills:

        skill_data = {
            "skill_name": skill["skill_name"],
            "progress": skill["progress_percentage"]
        }

        if skill["progress_percentage"] == 100:
            completed.append(skill_data)

        elif skill["progress_percentage"] > 0:
            in_progress.append(skill_data)

        else:
            not_started.append(skill_data)

    # Calculate overall progress
    total_skills = len(skills)

    overall_progress = sum(
        skill["progress_percentage"] for skill in skills
    ) / total_skills

    return {
        "student": dict(student),
        "career": dict(role),

        "learning_summary": {
            "total_skills": total_skills,
            "completed_skills": len(completed),
            "in_progress_skills": len(in_progress),
            "not_started_skills": len(not_started),
            "overall_progress": round(overall_progress, 2)
        },

        "skills": {
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started
        }
    }