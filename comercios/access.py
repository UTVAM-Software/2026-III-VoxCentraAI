"""Tenant and branch scope helpers for the commerce management screens."""

from django.db.models import Exists, OuterRef, Q, Subquery

from accesos.models import AlcanceSucursal, MembresiaComercio
from comercios.models import Comercio, Sucursal


def accessible_commerces(user):
    """Return only active commerce memberships for the signed-in user."""
    if not getattr(user, "is_authenticated", False):
        return Comercio.objects.none()
    if user.is_superuser:
        return Comercio.objects.all()
    return Comercio.objects.filter(
        membresias__usuario=user,
        membresias__activo=True,
    ).distinct()


def accessible_sucursales(user):
    """Apply membership scope; memberships without branch rows cover all branches."""
    if not getattr(user, "is_authenticated", False):
        return Sucursal.objects.none()
    if user.is_superuser:
        return Sucursal.objects.all()

    memberships = MembresiaComercio.objects.filter(usuario=user, activo=True)
    scoped_memberships = AlcanceSucursal.objects.filter(
        membresia_id=OuterRef("pk")
    )
    unrestricted_commerces = memberships.annotate(
        has_branch_scope=Exists(scoped_memberships)
    ).filter(has_branch_scope=False).values("comercio_id")
    explicitly_allowed_branches = AlcanceSucursal.objects.filter(
        membresia__in=memberships
    ).values("sucursal_id")

    return Sucursal.objects.filter(
        Q(comercio_id__in=Subquery(unrestricted_commerces))
        | Q(pk__in=Subquery(explicitly_allowed_branches))
    ).distinct()


def commerces_with_unrestricted_branch_access(user):
    """Return memberships that can create new branches for their commerce."""
    if not getattr(user, "is_authenticated", False):
        return Comercio.objects.none()
    if user.is_superuser:
        return Comercio.objects.all()

    memberships = MembresiaComercio.objects.filter(usuario=user, activo=True)
    branch_scope = AlcanceSucursal.objects.filter(membresia_id=OuterRef("pk"))
    unrestricted_ids = memberships.annotate(
        has_branch_scope=Exists(branch_scope)
    ).filter(has_branch_scope=False).values("comercio_id")
    return Comercio.objects.filter(pk__in=Subquery(unrestricted_ids))


def queryset_for_user(queryset, user, commerce_lookup):
    """Filter an object's commerce relation through active memberships."""
    if not getattr(user, "is_authenticated", False):
        return queryset.none()
    if user.is_superuser:
        return queryset
    return queryset.filter(
        **{f"{commerce_lookup}__in": accessible_commerces(user).values("pk")}
    )
