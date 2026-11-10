## =============================================================================
## script.py.mako - the stencil Alembic uses to write every NEW migration file.
##
## You never run this file. When you type "alembic revision -m ...", Alembic fills
## in the ${...} blanks below and saves the result as a new file in migrations/versions/.
##
## Lines that start with ## are notes for people: they are NOT copied into the new file.
##
## The blanks, and what Alembic puts in them:
##   ${message}       the text you gave after -m (becomes the file's first line)
##   ${up_revision}   the id of the new migration (for example 0002)
##   ${down_revision} the id of the migration it follows (for example 0001); this link builds the history chain
##   ${create_date}   when the file was written
##   ${imports}       extra import lines, added only when the changes need them
##   ${upgrades}      the changes that move the database forward ("pass" when empty)
##   ${downgrades}    the changes that undo them ("pass" when empty)
## =============================================================================
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

## The identifiers below are what chain the migrations together. Never change them by hand
## once a migration has been applied to any database.
# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


## "upgrade" runs when the database moves forward to this revision.
def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


## "downgrade" runs when the database is rolled back to the previous revision.
def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}