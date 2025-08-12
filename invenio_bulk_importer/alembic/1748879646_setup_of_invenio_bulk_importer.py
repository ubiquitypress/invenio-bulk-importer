#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Setup of invenio bulk importer."""

# revision identifiers, used by Alembic.
revision = "1748879646"
down_revision = None
branch_labels = ("invenio_bulk_importer",)
depends_on = None


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
