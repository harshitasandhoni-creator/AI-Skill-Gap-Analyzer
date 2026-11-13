
-- =========================================
-- PROGRESS TRACKING TABLES
-- =========================================

-- 1. Students Table

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- 2. Student Resource Progress Table

CREATE TABLE IF NOT EXISTS student_resource_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    resource_id INTEGER NOT NULL,

    status TEXT NOT NULL DEFAULT 'Not Started'
        CHECK (
            status IN (
                'Not Started',
                'In Progress',
                'Completed'
            )
        ),

    started_at TEXT,
    completed_at TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id),

    FOREIGN KEY (role_id)
        REFERENCES roles(role_id),

    FOREIGN KEY (resource_id)
        REFERENCES learning_resources(resource_id),

    UNIQUE (student_id, role_id, resource_id)
);


-- 3. Indexes for faster progress queries

CREATE INDEX IF NOT EXISTS
idx_student_resource_progress
ON student_resource_progress(student_id, role_id);

CREATE INDEX IF NOT EXISTS
idx_resource_progress_resource
ON student_resource_progress(resource_id);
