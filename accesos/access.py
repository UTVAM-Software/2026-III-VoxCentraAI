"""Tenant and branch scoping helpers shared by the management views."""

from django.db.models import Exists, OuterRef, Q, Subquery

from accesos.models import AlcanceSucursal, MembresiaComercio
from comercios.models import Comercio, Sucursal


def accessible_commerces(user):
    """Return the active commerce memberships available to ``user``."""
    if not getattr(user, "is_authenticated", False):
        return Comercio.objects.none()
    if user.is_superuser:
        return Comercio.objects.all()
    return Comercio.objects.filter(
        membresias__usuario=user,
        membresias__activo=True,
    ).distinct()


def accessible_sucursales(user):
    """Apply active memberships and their optional branch restrictions."""
    if not getattr(user, "is_authenticated", False):
        return Sucursal.objects.none()
    if user.is_superuser:
        return Sucursal.objects.all()

    memberships = MembresiaComercio.objects.filter(usuario=user, activo=True)
    branch_scopes = AlcanceSucursal.objects.filter(membresia_id=OuterRef("pk"))
    unrestricted_commerces = (
        memberships.annotate(has_branch_scope=Exists(branch_scopes))
        .filter(has_branch_scope=False)
        .values("comercio_id")
    )
    allowed_branches = AlcanceSucursal.objects.filter(
        membresia__in=memberships
    ).values("sucursal_id")

    return Sucursal.objects.filter(
        Q(comercio_id__in=Subquery(unrestricted_commerces))
        | Q(pk__in=Subquery(allowed_branches))
    ).distinct()


def queryset_for_user(queryset, user, commerce_lookup):
    """Limit a queryset by an ORM path from each row to its commerce."""
    if not getattr(user, "is_authenticated", False):
        return queryset.none()
    if user.is_superuser:
        return queryset
    return queryset.filter(
        **{f"{commerce_lookup}__in": accessible_commerces(user)}
    ).distinct()


def scoped_queryset(
    queryset,
    user,
    *,
    commerce_lookup=None,
    branch_lookup=None,
    branch_scope=False,
    nullable_branch=False,
):
    """Apply commerce and branch scope; fail closed without a declared scope."""
    if not getattr(user, "is_authenticated", False):
        return queryset.none()
    if user.is_superuser:
        return queryset

    if commerce_lookup:
        queryset = queryset_for_user(queryset, user, commerce_lookup)
    if branch_scope:
        queryset = queryset.filter(pk__in=accessible_sucursales(user))
    if branch_lookup:
        branch_filter = {f"{branch_lookup}__in": accessible_sucursales(user)}
        if nullable_branch:
            queryset = queryset.filter(
                Q(**{f"{branch_lookup}__isnull": True}) | Q(**branch_filter)
            )
        else:
            queryset = queryset.filter(**branch_filter)

    if not (commerce_lookup or branch_scope or branch_lookup):
        return queryset.none()
    return queryset.distinct()
