from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accesos.access import scoped_queryset


class PermissionRequiredLoginMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Redirect anonymous users and return 403 for authenticated users without permission."""

    raise_exception = False
    superuser_only = False

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()

    def has_permission(self):
        if self.superuser_only and not self.request.user.is_superuser:
            return False
        return super().has_permission()


class ScopedQuerysetMixin:
    commerce_lookup = None
    branch_lookup = None
    branch_scope = False
    nullable_branch = False

    def get_queryset(self):
        queryset = super().get_queryset()
        return scoped_queryset(
            queryset,
            self.request.user,
            commerce_lookup=self.commerce_lookup,
            branch_lookup=self.branch_lookup,
            branch_scope=self.branch_scope,
            nullable_branch=self.nullable_branch,
        )


class ManagedListView(PermissionRequiredLoginMixin, ScopedQuerysetMixin, ListView):
    template_name = "accesos/crud/object_list.html"
    list_fields = ()
    list_url_name = ""
    create_url_name = ""
    update_url_name = ""
    delete_url_name = ""

    def action_urls(self, obj):
        return {
            "edit_url": reverse(self.update_url_name, kwargs={"pk": obj.pk}),
            "delete_url": reverse(self.delete_url_name, kwargs={"pk": obj.pk}),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        context["title"] = model._meta.verbose_name_plural.capitalize()
        context["list_url"] = reverse(self.list_url_name)
        context["create_url"] = reverse(self.create_url_name)
        add_permission = f"{model._meta.app_label}.add_{model._meta.model_name}"
        change_permission = f"{model._meta.app_label}.change_{model._meta.model_name}"
        delete_permission = f"{model._meta.app_label}.delete_{model._meta.model_name}"
        context["can_create"] = self.request.user.has_perm(add_permission) and (
            not self.superuser_only or self.request.user.is_superuser
        )
        context["columns"] = [
            model._meta.get_field(field_name).verbose_name.capitalize()
            for field_name in self.list_fields
        ]
        context["rows"] = []
        for obj in context["object_list"]:
            urls = self.action_urls(obj)
            context["rows"].append(
                {
                    "values": [getattr(obj, field_name) for field_name in self.list_fields],
                    "edit_url": (
                        urls["edit_url"]
                        if self.request.user.has_perm(change_permission)
                        else None
                    ),
                    "delete_url": (
                        urls["delete_url"]
                        if self.request.user.has_perm(delete_permission)
                        and (not self.superuser_only or self.request.user.is_superuser)
                        else None
                    ),
                }
            )
        return context


class ManagedCreateView(PermissionRequiredLoginMixin, CreateView):
    template_name = "accesos/crud/object_form.html"
    list_url_name = ""
    page_title = ""
    set_user_field = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.set_user_field:
            setattr(form.instance, self.set_user_field, self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class ManagedUpdateView(
    PermissionRequiredLoginMixin, ScopedQuerysetMixin, UpdateView
):
    template_name = "accesos/crud/object_form.html"
    list_url_name = ""
    page_title = ""

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class ManagedDeleteView(
    PermissionRequiredLoginMixin, ScopedQuerysetMixin, DeleteView
):
    template_name = "accesos/crud/object_confirm_delete.html"
    list_url_name = ""
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.page_title
        context["list_url"] = reverse(self.list_url_name)
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


def build_crud_views(
    model,
    form_class,
    list_url_name,
    page_title,
    *,
    commerce_lookup=None,
    branch_lookup=None,
    nullable_branch=False,
    superuser_only=False,
    set_user_field=None,
):
    """Create consistent views with explicit permissions and tenant scoping."""
    scope = {
        "commerce_lookup": commerce_lookup,
        "branch_lookup": branch_lookup,
        "nullable_branch": nullable_branch,
        "superuser_only": superuser_only,
    }
    return (
        ManagedCreateView.as_view(
            model=model,
            form_class=form_class,
            permission_required=f"{model._meta.app_label}.add_{model._meta.model_name}",
            list_url_name=list_url_name,
            page_title=f"Crear {page_title.lower()}",
            set_user_field=set_user_field,
            superuser_only=superuser_only,
        ),
        ManagedUpdateView.as_view(
            model=model,
            form_class=form_class,
            permission_required=f"{model._meta.app_label}.change_{model._meta.model_name}",
            list_url_name=list_url_name,
            page_title=f"Editar {page_title.lower()}",
            **scope,
        ),
        ManagedDeleteView.as_view(
            model=model,
            permission_required=f"{model._meta.app_label}.delete_{model._meta.model_name}",
            list_url_name=list_url_name,
            page_title=f"Eliminar {page_title.lower()}",
            **scope,
        ),
    )
