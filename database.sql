-- ============================================================
--  Smart Attendance System Using Face Recognition
--  Database Setup Script
--  Run this in phpMyAdmin or MySQL command line
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_attendance_db;
USE smart_attendance_db;

-- ── Students Table ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    student_id    INT          AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    roll_no       VARCHAR(20)  UNIQUE NOT NULL,
    class         VARCHAR(30)  NOT NULL,
    email         VARCHAR(150) UNIQUE,
    phone         VARCHAR(15),
    image_path    VARCHAR(255),
    registered_on DATETIME     DEFAULT NOW()
);

-- ── Faculty Table ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id  INT          AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    department  VARCHAR(100) DEFAULT 'Computer Science',
    created_on  DATETIME     DEFAULT NOW()
);

-- ── Subjects Table ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subjects (
    subject_id  INT          AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(20)  UNIQUE NOT NULL,
    semester    INT          DEFAULT 1,
    faculty_id  INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE SET NULL
);

-- ── Attendance Table ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance (
    att_id      INT         AUTO_INCREMENT PRIMARY KEY,
    student_id  INT         NOT NULL,
    subject_id  INT         NOT NULL,
    date        DATE        NOT NULL,
    time        TIME        NOT NULL,
    status      VARCHAR(10) DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    UNIQUE KEY no_dup (student_id, subject_id, date)
);

-- ── Notifications Table ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    notif_id    INT          AUTO_INCREMENT PRIMARY KEY,
    student_id  INT          NOT NULL,
    message     TEXT,
    sent_at     DATETIME     DEFAULT NOW(),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ── Default Admin Faculty Account ───────────────────────────
-- Password: admin123  (stored as plain text for simplicity)
INSERT IGNORE INTO faculty (name, email, password, department)
VALUES ('Administrator', 'admin@college.com', 'admin123', 'Computer Science');

-- ── Sample Subject ──────────────────────────────────────────
INSERT IGNORE INTO subjects (name, code, semester, faculty_id)
VALUES ('Data Structures', 'CS201', 4, 1),
       ('Computer Networks', 'CS202', 4, 1),
       ('Python Programming', 'CS203', 4, 1);

-- ============================================================
--  Done! Open phpMyAdmin > smart_attendance_db to verify.
-- ============================================================
