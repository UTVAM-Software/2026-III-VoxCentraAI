from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView

from .forms import (
    AuthUserChangeForm,
    AuthUserCreationForm,
    AuthUserPasswordForm,
    GroupForm,
    PermissionForm,
    VoxcentraAuthenticationForm,
)


User = get_user_model()


class LoginPageView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    authentication_form = VoxcentraAuthenticationForm


class LogoutPageView(LogoutView):
    template_name = 'registration/logged_out.html'


class SuperuserRequiredMixin(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
):
    """Exige sesión, permiso Django del recurso y una cuenta superusuario."""

    login_url = 'cuentas:login'
    raise_exception = True

    def test_func(self):
        return self.request.user.is_superuser


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'cuentas:login'
    template_name = 'cuentas/dashboard.html'


class AuthRecordListView(SuperuserRequiredMixin, ListView):
    template_name = 'cuentas/object_list.html'
    context_object_name = 'records'
    title = ''
    create_url_name = ''
    edit_url_name = ''
    delete_url_name = ''
    show_user_controls = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=self.title,
            create_url_name=self.create_url_name,
            edit_url_name=self.edit_url_name,
            delete_url_name=self.delete_url_name,
            show_user_controls=self.show_user_controls,
        )
        return context


class AuthRecordCreateView(SuperuserRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'cuentas/object_form.html'
    title = ''
    cancel_url_name = ''
    success_message = 'El registro se creó correctamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(title=self.title, cancel_url_name=self.cancel_url_name)
        return context


class AuthRecordUpdateView(SuperuserRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'cuentas/object_form.html'
    title = ''
    cancel_url_name = ''
    success_message = 'Los cambios se guardaron correctamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(title=self.title, cancel_url_name=self.cancel_url_name)
        return context


class AuthRecordDeleteView(SuperuserRequiredMixin, DeleteView):
    template_name = 'cuentas/object_confirm_delete.html'
    success_message = 'El registro se eliminó correctamente.'
    cancel_url_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(cancel_url_name=self.cancel_url_name)
        return context

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class UserListView(AuthRecordListView):
    model = User
    permission_required = 'auth.view_user'
    title = 'Usuarios'
    create_url_name = 'cuentas:user_create'
    edit_url_name = 'cuentas:user_update'
    delete_url_name = 'cuentas:user_delete'
    show_user_controls = True


class UserCreateView(AuthRecordCreateView):
    model = User
    form_class = AuthUserCreationForm
    permission_required = 'auth.add_user'
    success_url = reverse_lazy('cuentas:user_list')
    title = 'Crear usuario'
    cancel_url_name = 'cuentas:user_list'


class UserUpdateView(AuthRecordUpdateView):
    model = User
    form_class = AuthUserChangeForm
    permission_required = 'auth.change_user'
    success_url = reverse_lazy('cuentas:user_list')
    title = 'Editar usuario'
    cancel_url_name = 'cuentas:user_list'


class UserDeleteView(AuthRecordDeleteView):
    model = User
    permission_required = 'auth.delete_user'
    success_url = reverse_lazy('cuentas:user_list')
    cancel_url_name = 'cuentas:user_list'
    success_message = 'El usuario se eliminó correctamente.'

    def get_queryset(self):
        return super().get_queryset().filter(is_superuser=False).exclude(pk=self.request.user.pk)


class UserPasswordChangeView(SuperuserRequiredMixin, SuccessMessageMixin, FormView):
    form_class = AuthUserPasswordForm
    template_name = 'cuentas/object_form.html'
    permission_required = 'auth.change_user'
    success_url = reverse_lazy('cuentas:user_list')
    success_message = 'La contraseña se cambió correctamente.'
    title = 'Cambiar contraseña'
    cancel_url_name = 'cuentas:user_list'

    def get_account(self):
        return get_object_or_404(
            User.objects.filter(is_superuser=False),
            pk=self.kwargs['pk'],
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_account()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(title=self.title, cancel_url_name=self.cancel_url_name)
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class GroupListView(AuthRecordListView):
    model = Group
    permission_required = 'auth.view_group'
    title = 'Grupos'
    create_url_name = 'cuentas:group_create'
    edit_url_name = 'cuentas:group_update'
    delete_url_name = 'cuentas:group_delete'


class GroupCreateView(AuthRecordCreateView):
    model = Group
    form_class = GroupForm
    permission_required = 'auth.add_group'
    success_url = reverse_lazy('cuentas:group_list')
    title = 'Crear grupo'
    cancel_url_name = 'cuentas:group_list'


class GroupUpdateView(AuthRecordUpdateView):
    model = Group
    form_class = GroupForm
    permission_required = 'auth.change_group'
    success_url = reverse_lazy('cuentas:group_list')
    title = 'Editar grupo'
    cancel_url_name = 'cuentas:group_list'


class GroupDeleteView(AuthRecordDeleteView):
    model = Group
    permission_required = 'auth.delete_group'
    success_url = reverse_lazy('cuentas:group_list')
    cancel_url_name = 'cuentas:group_list'
    success_message = 'El grupo se eliminó correctamente.'


class PermissionListView(AuthRecordListView):
    model = Permission
    permission_required = 'auth.view_permission'
    title = 'Permisos'
    create_url_name = 'cuentas:permission_create'
    edit_url_name = 'cuentas:permission_update'
    delete_url_name = 'cuentas:permission_delete'


class PermissionCreateView(AuthRecordCreateView):
    model = Permission
    form_class = PermissionForm
    permission_required = 'auth.add_permission'
    success_url = reverse_lazy('cuentas:permission_list')
    title = 'Crear permiso'
    cancel_url_name = 'cuentas:permission_list'


class PermissionUpdateView(AuthRecordUpdateView):
    model = Permission
    form_class = PermissionForm
    permission_required = 'auth.change_permission'
    success_url = reverse_lazy('cuentas:permission_list')
    title = 'Editar permiso'
    cancel_url_name = 'cuentas:permission_list'


class PermissionDeleteView(AuthRecordDeleteView):
    model = Permission
    permission_required = 'auth.delete_permission'
    success_url = reverse_lazy('cuentas:permission_list')
    cancel_url_name = 'cuentas:permission_list'
    success_message = 'El permiso se eliminó correctamente.'
