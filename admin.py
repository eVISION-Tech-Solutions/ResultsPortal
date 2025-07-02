from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Institution, Teacher, Student, Result
from .forms import InstitutionCreationForm  # if you made a custom one
from django.utils.translation import gettext_lazy as _

@admin.register(Institution)
class InstitutionAdmin(UserAdmin):
    model = Institution
    list_display = ['id', 'name']
    search_fields = ['name']
    ordering = ['id']
    
    fieldsets = (
        (None, {'fields': ('name', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'password1', 'password2'),
        }),
    )

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'institution']
    search_fields = ['name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'institution']
    search_fields = ['name']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'teacher', 'subject', 'score']
    list_filter = ['teacher', 'subject']
    search_fields = ['student__name', 'student__admission_number']

