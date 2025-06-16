# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Ubiquity Press
#
# Invenio-Bulk-Importer is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit of Work decorator for bulk importer service methods."""

from functools import wraps

from invenio_db.shared import db
from invenio_records_resources.services.uow import UnitOfWork


def rollabck_unit_of_work(**kwargs):
    """Decorator to auto-inject a unit of work if not provided.

    If no unit of work is provided, this decorator will create a new unit of
    work and commit it after the function has been executed.

    .. code-block:: python

        @unit_of_work()
        def aservice_method(self, ...., uow=None):
            # ...
            uow.register(...)

    """

    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            if "uow" not in kwargs or kwargs["uow"] is None:
                # Migration path - start a UoW and always rollback
                with UnitOfWork(db.session) as uow:
                    kwargs["uow"] = uow
                    res = f(self, *args, **kwargs)
                    uow.rollback()
                    return res
            else:
                return f(self, *args, **kwargs)

        return inner

    return decorator
