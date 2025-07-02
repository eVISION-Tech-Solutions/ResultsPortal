from django.urls import path
from . import views
from .views import results_collection_view, update_result,enter_results, lookup_student

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register_institution, name='register'),
    path('login/', views.login_institution, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-teacher/', views.add_teacher, name='add_teacher'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-result/', views.add_result, name='add_result'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('results-collection/', results_collection_view, name='results_collection'),
    path('update-result/<int:result_id>/', update_result, name='update_result'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('lookup/', views.lookup_student, name='lookup_student'),
    path('enter-results/<int:student_id>/', views.enter_results, name='enter_results'),
    path('logout/', views.logout_view, name='logout'),
]
