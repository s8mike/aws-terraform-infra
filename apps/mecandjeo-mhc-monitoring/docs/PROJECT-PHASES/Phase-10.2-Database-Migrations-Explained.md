# Database Migrations Explained

This guide explains how the database structure is created and changed in this project, why it is done with Alembic, and what each migration file does. It assumes no earlier knowledge. Everything here was run and verified in Phase 11B on PostgreSQL.

Commands are for **Git Bash** and run from `apps/mecandjeo-mhc-monitoring` unless stated.

## Contents

1. The idea in plain words
2. Two things called "migration" (and do we copy local data?)
3. Why migrations, why Alembic, and is it tied to one database?
4. Every migration-related file and what it does
5. `alembic.ini` explained
6. `script.py.mako` explained
7. `0001_baseline.py` and the history chain
8. The `crane-migrate` job and why it exits
9. Everyday commands
10. Adding a migration (the verified workflow)
11. From your laptop to the cloud
12. What Phase 11B proved
13. FAQ and troubleshooting

---

## 1. The idea in plain words

A database has a **structure** (called the *schema*): which tables exist, which columns each table has, which columns must be unique, and so on. The application only works if the database has exactly the structure the code expects.

A **migration** is a small numbered file that describes one change to that structure ("create these tables", "add a `berth` column to `cranes`"). **Alembic** is the tool that runs these files, in order, and remembers which one was run last (in a table called `alembic_version`).

Think of blueprint revisions for a building: revision 1 is the first plan, revision 2 adds a room. Anyone holding the same set of revisions can build the same building. Or think of Git, but for the database structure instead of the code.

## 2. Two things called "migration"

|                    | Schema migration                            | Data migration                     |
|--------------------|---------------------------------------------|------------------------------------|
| What moves         | The **structure**: tables, columns, indexes | The **rows**: users, shifts, tasks |
| Tool here          | Alembic                                     | Not used                           |
| Done in Phase 11B? | **Yes**                                     | **No**                             |

Everything in Phase 11B was a schema migration. The `alembic stamp head` command you ran in Option A copied no data: 

```bash
docker compose --env-file .env.docker build crane-app
docker compose --env-file .env.docker run --rm crane-migrate alembic stamp head
docker compose --env-file .env.docker run --rm crane-migrate alembic current
docker compose --env-file .env.docker run --rm crane-migrate alembic check
docker compose --env-file .env.docker up -d --build
```

it only wrote "this database is at revision 0001" into `alembic_version`.

### Must the local data be migrated to the cloud?

**No.** Local data is demo and test data created by the seed script, including operators, tasks, and delays.

A cloud database should:

1. Start empty.
2. Build its structure with `alembic upgrade head`.
3. Receive the standard reference values and the first admin account through the bootstrap step.
4. Collect real data from real users.

If you ever need to move local rows elsewhere, these are the options:

#### Data migration options

1. **Start empty (recommended)**
   - **Use it when:** Production and any real environment.
   - **Notes:** Cleanest approach; there is nothing to clean up.

2. **Run the seed script**
   - **Use it when:** Setting up a demo or test environment.
   - **Notes:** Creates demo accounts with a shared password. Never use it in production.

3. **Use `pg_dump` and restore**
   - **Use it when:** Moving a whole copy of a database at the same migration revision.
   - **Notes:** The `~/backup_before_phase11.sql` file you created is this kind of backup. It contains password hashes, so keep it out of the repository and delete it when no longer needed.

4. **Use a custom copy script**
   - **Use it when:** Moving only selected tables.
   - **Notes:** Requires care with IDs and relationships.
                           |


## 3. Why migrations, why Alembic, and is it tied to one database?

### The problem they solve

Before Phase 11B the tables were created by `Base.metadata.create_all(...)`. That call only creates tables that are **missing**. It never changes a table that already exists. So if a developer adds a column to a model, an existing database silently stays old, and the code breaks against it. In the cloud you cannot wipe the database at each release, so you need a safe, repeatable way to change an existing database. Migrations are that way, and the same files give every environment (your laptop, a colleague's, the cloud) the same structure.

### The options

1. **`create_all` (before)**
   - **Changes existing tables?** No.
   - **Remembers the version?** No.
   - **Same everywhere?** Only for new databases.

2. **Hand-written SQL scripts**
   - **Changes existing tables?** Yes.
   - **Remembers the version?** Only if you track it by hand.
   - **Same everywhere?** Easy to get wrong.

3. **Alembic (now)**
   - **Changes existing tables?** Yes.
   - **Remembers the version?** Yes (`alembic_version`).
   - **Same everywhere?** Yes.

4. **Other tools (Flyway, Liquibase, Django or Prisma migrations)**
   - **Changes existing tables?** Yes.
   - **Remembers the version?** Yes.
   - **Same everywhere?** Yes, but built for other languages or frameworks.

### Why Alembic

- It is the standard migration tool for **SQLAlchemy**, which this project already uses. They share an author and work together.
- It reads our models and writes the migration for you (`--autogenerate`), then `alembic check` and the test suite prove the models and the migrations agree.
- It can go forward (`upgrade`), back (`downgrade`), and print the exact SQL it would run (`--sql`).

### Is it tied to a database type?

**No.** Alembic works with any database SQLAlchemy supports: PostgreSQL, MySQL and MariaDB, SQLite, Microsoft SQL Server and Oracle. It is tied to Python and SQLAlchemy, not to a database. Small differences between databases are handled for you; for example, `env.py` turns on "batch mode" for SQLite, which cannot change tables in place, and PostgreSQL ignores that setting. We checked PostgreSQL specifically: the SQL the baseline produces is identical to what the models alone would create (13 tables, 17 indexes).

## 4. Every migration-related file and what it does

1. **`alembic.ini`**
   - **Kind:** Settings file
   - **What it does:** Tells Alembic where the migration folder is, how files are named, and how to log. Holds **no** database address.
   - **Edit it?** Rarely.

2. **`migrations/env.py`**
   - **Kind:** Python
   - **What it does:** Connects Alembic to our app: reads the database address (`DATABASE_URL`), loads the models so Alembic knows the expected tables, and runs the migrations.
   - **Edit it?** Rarely.

3. **`migrations/script.py.mako`**
   - **Kind:** Template
   - **What it does:** The stencil Alembic uses to write each new migration file.
   - **Edit it?** Rarely.

4. **`migrations/versions/`**
   - **Kind:** Folder
   - **What it does:** Contains one file per change, forming the migration history.
   - **Edit it?** Add files.

5. **`migrations/versions/0001_baseline.py`**
   - **Kind:** Python
   - **What it does:** The first migration; creates all 13 tables.
   - **Edit it?** Never, once applied anywhere.

6. **`tests/test_migrations.py`**
   - **Kind:** Tests
   - **What it does:** Contains 6 tests verifying that migrations build exactly the schema described by the models, can be undone, can be repeated, form one straight history, adopt an existing database, and refuse an unstamped one.
   - **Edit it?** When behavior changes.

7. **`tests/test_lifespan.py`**
   - **Kind:** Tests
   - **What it does:** Contains 4 tests verifying that start-up creates tables and runs the bootstrap independently, in the right order.
   - **Edit it?** When behavior changes.

8. **`app/db/bootstrap.py`**
   - **Kind:** Python
   - **What it does:** After the tables exist, loads the 28 reference values, sample cranes, and the first admin. Safe to repeat.
   - **Edit it?** Seldom.

9. **`app/config.py`**
   - **Kind:** Python
   - **What it does:** Defines `AUTO_CREATE_SCHEMA` and `RUN_BOOTSTRAP`.
   - **Edit it?** When adding settings.

10. **`app/main.py`**
    - **Kind:** Python
    - **What it does:** At start-up, creates tables only if `AUTO_CREATE_SCHEMA` is on and runs the bootstrap only if `RUN_BOOTSTRAP` is on.
    - **Edit it?** Seldom.

11. **`Dockerfile`**
    - **Kind:** Docker
    - **What it does:** Copies `alembic.ini` and `migrations/` into the image.
    - **Edit it?** Seldom.

12. **`docker-compose.yml`**
    - **Kind:** Docker
    - **What it does:** Defines the `crane-migrate` job and the start order.
    - **Edit it?** Seldom.

13. **`requirements.txt`**
    - **Kind:** Packages
    - **What it does:** Includes `alembic`.
    - **Edit it?** When adding packages.

14. **`.env.docker`**
    - **Kind:** Settings
    - **What it does:** Sets `AUTO_CREATE_SCHEMA=false` and `RUN_BOOTSTRAP=true`.
    - **Edit it?** Per machine.

15. **`alembic_version`**
    - **Kind:** A **table in the database**
    - **What it does:** Holds one row containing the current revision (for example, `0001`).
    - **Edit it?** Never by hand.


## 5. `alembic.ini` explained

`.ini` stands for "initialization file". It is a plain text settings file, an old and simple format: names in `[square brackets]` start a section, and each line below is `key = value`. It is not code. Alembic reads it when you run any `alembic` command.

```ini
[alembic]
script_location = %(here)s/migrations
file_template = %%(rev)s_%%(slug)s
prepend_sys_path = .
path_separator = os
```

| Line               | Meaning                                                                                      |
|--------------------|----------------------------------------------------------------------------------------------|
| `script_location`  | Where `env.py` and the `versions` folder live. `%(here)s` means "the folder this file is in" |
| `file_template`    | Names new files like `0002_add_berth_to_cranes.py` (revision id, then the message)           |
| `prepend_sys_path` | Lets `env.py` import our `app` package                                                       |
| `path_separator`   | How multiple paths would be separated (unused here)                                          |

The other sections (`[loggers]`, `[handlers]`, `[formatters]` and the ones named after them) only control how Alembic's messages are printed. The database address is deliberately **not** here: `env.py` reads it from `DATABASE_URL`, so the same file works on a laptop and in the cloud without any secrets inside it.

## 6. `script.py.mako` explained

`.mako` is the file type of **Mako**, a small Python templating tool. A template is a stencil with blanks. You never run this file. When you type `alembic revision -m "add berth"`, Alembic fills in the blanks and saves the result as a new `.py` file in `migrations/versions/`.

Lines starting with `##` are notes in the template; they never appear in the generated file. The blanks look like `${name}`:

| Blank              | What Alembic puts there                    | Example               |
|--------------------|--------------------------------------------|-----------------------|
| `${message}`       | The text after `-m`                        | `add berth to cranes` |
| `${up_revision}`   | The new migration's id                     | `0002`                |
| `${down_revision}` | The id of the migration before it          | `0001`                |
| `${create_date}`   | When the file was written                  | `2026-10-24 20:45:42` |
| `${imports}`       | Extra import lines, only if needed         | (usually empty)       |
| `${upgrades}`      | The changes that move the database forward | `op.add_column(...)`  |
| `${downgrades}`    | The changes that undo them                 | `op.drop_column(...)` |

The template with its explanatory notes is in `migrations/script.py.mako`.

**From stencil to file.** For `alembic revision --autogenerate -m "add berth to cranes" --rev-id 0002`, after adding a `berth` column to the `Crane` model, the generated file looks like this (shortened):

```python
"""add berth to cranes

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24 20:45:42

"""
revision: str = '0002'
down_revision = '0001'

def upgrade() -> None:
    with op.batch_alter_table('cranes', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('berth', sa.String(length=50), nullable=True)
        )

def downgrade() -> None:
    with op.batch_alter_table('cranes', schema=None) as batch_op:
        batch_op.drop_column('berth')
```

You do not write this by hand: Alembic compares the models with the database and fills in `upgrade` and `downgrade`. You review it before using it.

## 7. `0001_baseline.py` and the history chain

### What the baseline is

The baseline is the **first migration**. It describes the whole structure the application had on the day migrations were introduced: all 13 tables, their columns, constraints and indexes. A brand-new, empty database runs it and ends up with the full structure. A database that already had those tables (like yours in Option A) is *stamped* instead, so the baseline is recorded as done without running.

### The history is a chain, not a pile

Each migration points to the one before it (`down_revision`). The database stores the id of the last one it applied.

```
(empty) -> 0001 baseline -> 0002 add berth -> 0003 next change
                                 ^
                 the database says: "I am at 0002"
```

### What happens when more tables are needed?

A new table or column **never** creates another baseline and **never** overwrites the first one. It becomes a **new migration file** (`0002`, `0003`, ...) that holds only that change.

#### Migration scenarios

1. **You add a model or column, then run `alembic revision --autogenerate`**
   - **What happens:** A new `0002` file holds just the difference. `0001` is untouched.

2. **You add a model or column and forget the migration**
   - **What happens:** `alembic check` and the test `test_migrations_build_the_schema_the_models_describe` fail and name the missing change.

3. **You deploy to a new, empty cloud database**
   - **What happens:** `alembic upgrade head` runs `0001`, then `0002`, then `0003`, in order, and ends with the same structure as your laptop.

4. **You deploy to a cloud database already at `0002`**
   - **What happens:** Only `0003` and later migrations run.

5. **Someone edits `0001` after it was applied somewhere**
   - **What happens:** **Do not.** Existing databases would never see the edit, so they would differ from new ones. Make a new migration instead.

6. **A table is created by hand with SQL, outside the models**
   - **What happens:** Alembic does not know about it; `alembic check` reports it as unexpected. Avoid manual structure changes.

7. **Two developers both create `0002`**
   - **What happens:** Alembic reports "multiple heads"; `test_history_has_a_single_head` catches it. Fix it with a merge revision.

Rule of thumb: **change the models, generate a migration, review it, commit both together.**

## 8. The `crane-migrate` job and why it exits

Most containers in this project are **servers**: they start and keep running (`crane-db`, `crane-app`, `crane-web`). `crane-migrate` is a **job**: it runs one command (`alembic upgrade head`), finishes, and the container stops. That is intended.

Start order:

```
crane-db (healthy)
   -> crane-migrate (runs, exits 0)
   -> crane-app (healthy)
   -> crane-web (healthy)
```

### Migration job configuration

1. **`command: ["alembic", "upgrade", "head"]`**
   - **Why:** Defines the one task the job performs.

2. **`restart: "no"`**
   - **Why:** Docker must not restart a job that has finished.

3. **`crane-app` waits with `service_completed_successfully`**
   - **Why:** The API starts only after the database structure is ready. If the migration job fails, the API does not start.

### How to read the migration job status

1. **`docker compose ps -a` shows `Exited (0)`**
   - **Meaning:** Success. The database is up to date.

2. **`docker compose ps -a` shows `Exited (1)` or another number**
   - **Meaning:** The migration failed. Read the logs:
     ```bash
     docker compose --env-file .env.docker logs crane-migrate
     ```

**Important notes:**

- `docker compose ps` without `-a` hides stopped containers, so the migration job appears to vanish.
- The migration job also runs again on every `up -d`. If the database is already up to date, running it again does nothing. This is exactly what you saw in the tests: the `Running upgrade` count stayed the same.

## 9. Everyday commands

Inside Docker, put the following prefix in front of each command:

```bash
docker compose --env-file .env.docker run --rm crane-migrate
```

### Alembic commands

1. **`alembic current`**
   - **What it does:** Shows which revision the database is at (`0001 (head)`).

2. **`alembic history`**
   - **What it does:** Lists the whole chain of migrations.

3. **`alembic heads`**
   - **What it does:** Shows the latest revision(s); there must be exactly one.

4. **`alembic upgrade head`**
   - **What it does:** Applies every migration not yet applied.

5. **`alembic upgrade head --sql`**
   - **What it does:** Prints the SQL instead of running it.

6. **`alembic downgrade -1`**
   - **What it does:** Undoes the latest migration.

7. **`alembic stamp head`**
   - **What it does:** Records "this database is at the latest revision" **without running anything**. Use it for a database whose tables already match.

8. **`alembic check`**
   - **What it does:** Fails if the models and the database differ; prints `No new upgrade operations detected.` when they agree.

9. **`alembic revision --autogenerate -m "text"`**
   - **What it does:** Writes a new migration from the difference.

## 10. Adding a migration (the verified workflow)

From `apps/mecandjeo-mhc-monitoring`, with the virtual environment active:

```bash
export DATABASE_URL=sqlite:///./scratch.db
alembic upgrade head
alembic revision --autogenerate -m "describe the change" --rev-id 0002
rm scratch.db
unset DATABASE_URL
```

Why a throwaway SQLite file: autogenerate needs a database that is at the *previous* revision, so it can see only the new difference. Then:

1. Open the new file in `migrations/versions/` and read it.
2. Run `python -m pytest tests -q`; the migration tests must pass.
3. Rebuild with `docker compose --env-file .env.docker up -d --build`. The `crane-migrate` job applies it on start.
4. Commit the model change and the migration together.

## 11. From your laptop to the cloud

The plan for Phase 12 and 13 follows from the design:

1. The cloud database (RDS PostgreSQL) starts **empty**.
2. A one-off task runs `alembic upgrade head`, which builds the structure from the migration files.
3. A second one-off task runs `python -m app.db.bootstrap`, which loads the reference values and the first admin from settings held in a secrets store.
4. The API starts. `AUTO_CREATE_SCHEMA` and `SEED_SAMPLE_DATA` stay off.
5. Every later release runs the new migrations first, then starts the new API.

No local data is copied, and no local database is touched.

## 12. What Phase 11B proved (Checks and Results)

1. **Baseline SQL for PostgreSQL versus the models' own SQL**
   - **Result:** Identical: 13 tables and 17 indexes.

2. **`alembic check` against your real PostgreSQL after `stamp`**
   - **Result:** `No new upgrade operations detected.`

3. **Option A: Adopt the existing database**
   - **Result:** Data kept; `alembic current` showed `0001 (head)`.

4. **Part B: Wipe, rebuild, and reseed**
   - **Result:** The baseline built the full structure on an empty PostgreSQL database, and the application worked.

5. **Running the migration job again**
   - **Result:** Nothing changed. The job is safe to repeat.

6. **Backend tests**
   - **Result:** 71 passed (61 earlier plus 10 new).

## 13. FAQ and troubleshooting

### 13.1. Common migration messages and issues

1. **Message: `Detected sequence named 'delay_logs_id_seq' as owned by integer column ... assuming SERIAL`**
   - **Meaning:** Alembic recognized PostgreSQL's automatic ID counters.
   - **Answer:** This is informational, not an error. Alembic is treating the columns as ordinary auto-numbered IDs.

2. **Message: `Target database is not up to date`**
   - **Meaning:** The database is behind the migration history.
   - **Resolution:** Run the migrations before generating a new one:

     ```bash
     alembic upgrade head
     ```

3. **Message: `... already exists` during `upgrade`**
   - **Meaning:** The database was built earlier but was never stamped with the baseline revision.
   - **Resolution:** If the existing tables match the baseline, record the current revision:

     ```bash
     alembic stamp head
     ```

4. **Message: `Multiple head revisions are present`**
   - **Meaning:** Two migration revisions follow the same earlier revision, creating multiple history branches.
   - **Resolution:** Create a merge revision, then run the migration tests.

5. **Message: `No config file 'alembic.ini' found`**
   - **Meaning:** Alembic cannot find its configuration file in the expected folder or container image.
   - **Resolution:** Check the Dockerfile `COPY` instructions and `.dockerignore` to ensure `alembic.ini` is included.

6. **Message: `alembic: command not found` in the container**
   - **Meaning:** The image may have been built before Alembic was added to `requirements.txt`.
   - **Resolution:** Rebuild the image so the dependency is installed.

7. **Message: `dependency failed to start: container crane-migrate exited (1)`**
   - **Meaning:** The migration job failed, preventing the dependent API container from starting.
   - **Resolution:** Inspect the migration logs:
   
     ```bash
     docker compose --env-file .env.docker logs crane-migrate
     ```

### 13.2. Frequently asked questions

8. **Do I still need `AUTO_CREATE_SCHEMA`?**
   - **Answer:** It is only needed to start the API locally without Docker or migrations. In Docker and in the cloud, it stays `false`.

9. **What does `down -v` do to migrations?**
   - **Answer:** It deletes the database volume. The next start runs the complete migration history again against an empty database.

10. **Can I delete `~/backup_before_phase11.sql`?**
    - **Answer:** Yes, once Phase 11 is finished. The file contains password hashes, so do not commit or share it.
