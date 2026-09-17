"""
Purpose:
    Perform a basic PostgreSQL connectivity smoke test by executing
    SELECT 1 and verifying the returned result.

    Exit with status code 1 if the connection or query fails, allowing
    automated checks to detect database connectivity failures.
"""

import sys

from sqlalchemy import text

from app.database import engine


# Execute a simple query to verify that PostgreSQL is reachable
# and can process a database request.
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        value = result.scalar()

        # Confirm the query returned the expected result.
        if value != 1:
            raise RuntimeError(f"Unexpected query result: {value}")

        # Report successful database connectivity and query execution.
        print("PostgreSQL connection successful!")
        print(f"Test query result: {value}")

# Handle connection, query, or result-validation failures.
except Exception as e:
    # Print the failure details to help troubleshoot the problem.
    print("PostgreSQL connection failed!")
    print(f"Error: {e}")

    # Return a nonzero exit code so scripts and CI detect failure.
    sys.exit(1)