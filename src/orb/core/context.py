"""Define the Context class."""
from enum import Enum

from .query import Query


class Ordering(Enum):
    """Define ordering options."""

    Asc = 'asc'
    Desc = 'desc'


class ReturnType(Enum):
    """Define return options."""

    Data = 'data'
    Records = 'records'


class Context:
    """Metadata class for tracking lookup options."""

    def __init__(
        self,
        *,
        distinct: list=None,
        fields: list=None,
        locale: str=None,
        limit: int=None,
        namespace: str=None,
        order: list=None,
        page: int=None,
        page_size: int=None,
        returning: ReturnType=ReturnType.Records,
        scope: dict=None,
        start: int=None,
        timezone: str=None,
        where: Query=None,
    ):
        self.distinct = distinct
        self.fields = fields
        self.locale = locale
        self._limit = limit
        self.namespace = namespace
        self.order = order
        self.page = page
        self.page_size = page_size
        self.returning = returning
        self.scope = scope or {}
        self._start = start
        self.timezone = timezone
        self.where = where

    def get_limit(self) -> int:
        """Return limit for this context."""
        return self.page_size or self._limit

    def get_start(self) -> int:
        """Return start index for this context."""
        if self.page:
            return (self.page - 1) * (self.limit or 0)
        return self._start

    def set_limit(self, limit: int=None):
        """Set limit for this context."""
        self._limit = limit

    def set_start(self, start: int=None):
        """Set start index for this context."""
        self._start = start

    limit = property(get_limit, set_limit)
    start = property(get_start, set_start)


def _merge_distinct(options: dict, base_context: Context) -> list:
    """Return distinct joined from option and base context."""
    try:
        distinct = options['distinct']
    except KeyError:
        distinct = base_context.distinct if base_context else None
    else:
        if type(distinct) is str:
            distinct = distinct.split(',')
    return distinct


def _merge_fields(options: dict, base_context: Context) -> list:
    """Return new fields based on input and context."""
    try:
        fields = options['fields']
    except KeyError:
        fields = base_context.fields if base_context else None
    else:
        if type(fields) is str:
            fields = fields.split(',')

        if fields and base_context and base_context.fields:
            base_fields = [f for f in base_context.fields if f not in fields]
            return fields + base_fields
    return fields


def _merge_limit(options: dict, base_context: Context) -> int:
    """Return new limit based on input and context."""
    try:
        return options['limit']
    except KeyError:
        return base_context._limit if base_context else None


def _merge_locale(options: dict, base_context: Context) -> str:
    """Return new locale based on input and context."""
    try:
        return options['locale']
    except KeyError:
        return base_context.locale if base_context else None


def _merge_namespace(options: dict, base_context: Context) -> str:
    """Return new namespace based on input and context."""
    try:
        return options['namespace']
    except KeyError:
        return base_context.namespace if base_context else None


def _merge_order(options: dict, base_context: Context) -> list:
    """Return new order based on input and context."""
    try:
        order = options['order']
    except KeyError:
        order = base_context.order if base_context else None
    else:
        if type(order) is str:
            order = [
                (
                    part.strip('+-'),
                    Ordering.Desc if part.startswith('-') else Ordering.Asc
                ) for part in order.split(',')
            ]
    return order


def _merge_page(options: dict, base_context: Context) -> int:
    """Return new page based on input and context."""
    try:
        return options['page']
    except KeyError:
        return base_context.page if base_context else None


def _merge_page_size(options: dict, base_context: Context) -> int:
    """Return new page size based on input and context."""
    try:
        return options['page_size']
    except KeyError:
        return base_context.page_size if base_context else None


def _merge_query(options: dict, base_context: Context) -> Query:
    """Return new query based on input and context."""
    try:
        query = options['where']
    except KeyError:
        query = base_context.where if base_context else None
    else:
        if query is not None and base_context:
            query &= base_context.where
    return query


def _merge_returning(options: dict, base_context: Context) -> ReturnType:
    """Return new returning based on input and context."""
    try:
        return options['returning']
    except KeyError:
        return base_context.returning if base_context else ReturnType.Records


def _merge_scope(options: dict, base_context: Context) -> dict:
    """Return new scope based on input and context."""
    try:
        scope = options['scope']
    except KeyError:
        scope = base_context.scope if base_context else None
    else:
        if scope and base_context:
            new_scope = {}
            new_scope.update(base_context.scope)
            new_scope.update(scope)
            return new_scope
    return scope


def _merge_start(options: dict, base_context: Context) -> int:
    """Return new start index based on input and context."""
    try:
        return options['start']
    except KeyError:
        return base_context._start if base_context else None


def _merge_timezone(options: dict, base_context: Context) -> str:
    """Return new timezone based on input and context."""
    try:
        return options['timezone']
    except KeyError:
        return base_context.timezone if base_context else None


def make_context(**options) -> Context:
    """Merge context options together."""
    base_context = options.get('context')
    return Context(
        distinct=_merge_distinct(options, base_context),
        fields=_merge_fields(options, base_context),
        locale=_merge_locale(options, base_context),
        limit=_merge_limit(options, base_context),
        namespace=_merge_namespace(options, base_context),
        order=_merge_order(options, base_context),
        page=_merge_page(options, base_context),
        page_size=_merge_page_size(options, base_context),
        returning=_merge_returning(options, base_context),
        scope=_merge_scope(options, base_context),
        start=_merge_start(options, base_context),
        timezone=_merge_timezone(options, base_context),
        where=_merge_query(options, base_context),
    )
