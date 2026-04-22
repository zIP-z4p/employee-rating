```mermaid
erDiagram
    DEPARTMENTS {
        UUID id PK
        VARCHAR name
        VARCHAR code "UNIQUE"
        VARCHAR description
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    EMPLOYEES {
        UUID id PK
        UUID department_id FK
        VARCHAR full_name
        VARCHAR email "UNIQUE"
        VARCHAR position
        DATE hire_date
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    RATING_METRICS {
        UUID id PK
        VARCHAR name
        ENUM category
        NUMERIC weight
        TEXT description
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    RATING_ENTRIES {
        UUID id PK
        UUID employee_id FK
        UUID reviewer_id FK "nullable"
        UUID metric_id FK
        DATE period
        NUMERIC score
        ENUM category
        TEXT comment
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    RATING_SNAPSHOTS {
        UUID id PK
        UUID employee_id FK
        DATE period
        NUMERIC total_score
        INT rank
        INT department_rank
        NUMERIC percentile
        NUMERIC delta_score "nullable"
        INT delta_rank "nullable"
    }

    %% Relationships
    DEPARTMENTS ||--o{ EMPLOYEES : "has"
    EMPLOYEES ||--o{ RATING_ENTRIES : "receives"
    RATING_METRICS ||--o{ RATING_ENTRIES : "used_in"
    EMPLOYEES ||--o{ RATING_SNAPSHOTS : "has"
