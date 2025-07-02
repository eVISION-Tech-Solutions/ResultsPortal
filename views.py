from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import *
from .models import Teacher, Result, Student, Institution, StudentResult
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponseRedirect

def home(request):
    return render(request, 'results/home.html')

def about(request):
    return render(request, 'results/about.html')

def register_institution(request):
    InstitutionModel = get_user_model()
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            if InstitutionModel.objects.filter(name=name).exists():
                messages.error(request, "Institution name already exists. Please pick another name.")
                return redirect('register')
            user = InstitutionModel.objects.create_user(name=name, password=password)
            messages.success(request, "Institution registered successfully 🎉")
            return redirect('login')
    else:
        form = InstitutionForm()
    return render(request, 'results/register.html', {'form': form})

def login_institution(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=name, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'results/login.html', {'form': form})

@login_required
def dashboard(request):
    teachers = Teacher.objects.filter(institution=request.user)
    return render(request, 'results/dashboard.html', {'teachers': teachers})

@login_required
def add_teacher(request):
    if request.method == 'POST':
        form = AddTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.institution = request.user  # assumes Institution is user
            raw_password = form.cleaned_data['password']
            teacher.set_password(raw_password)
            teacher.save()
            messages.success(request, 'Teacher added successfully.')
            return redirect('dashboard')
    else:
        form = AddTeacherForm()
    return render(request, 'results/add_teacher.html', {'form': form})

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']
            try:
                # First, get all teachers with this name
                teachers = Teacher.objects.filter(name=name)
                if teachers.count() > 1:
                    messages.error(request, "Multiple teachers found with this name. Please contact your administrator.")
                    return render(request, 'results/teacher_login.html', {'form': form})
                elif teachers.count() == 0:
                    messages.error(request, "Invalid credentials.")
                    return render(request, 'results/teacher_login.html', {'form': form})
                
                teacher = teachers.first()
                if teacher.check_password(password):
                    request.session['teacher_id'] = teacher.id
                    return redirect('lookup_student')
                else:
                    messages.error(request, "Invalid credentials.")
            except Exception as e:
                messages.error(request, "Invalid credentials.")
    else:
        form = TeacherLoginForm()
    return render(request, 'results/teacher_login.html', {'form': form})

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id, institution=request.user)
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
    return redirect('dashboard')

@login_required
def add_student(request):
    try:
        Institution.objects.get(id=request.user.id)
    except Institution.DoesNotExist:
        messages.error(request, "Institution account not found.")
        return redirect("")
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.institution = request.user
            student.save()
            messages.success(request, "Student added successfully 🎉")
            return redirect("dashboard")
    else:
        form = StudentForm()
    return render(request, 'results/add_student.html', {'form': form})

@login_required
def add_result(request):
    if hasattr(request.user, 'is_teacher') and request.user.is_teacher:
        teacher = request.user
        institution = teacher.institution
        if request.method == 'POST':
            form = ResultForm(request.POST)
            if form.is_valid():
                result = form.save(commit=False)
                result.added_by = teacher
                if result.student.institution == institution:
                    result.save()
                    messages.success(request, "Result added successfully.")
                    return redirect('add_result')
                else:
                    form.add_error(None, "This student doesn't belong to your institution.")
        else:
            form = ResultForm()
        form.fields['student'].queryset = Student.objects.filter(institution=institution)
        return render(request, 'results/add_result.html', {'form': form})
    else:
        return redirect('login')

@login_required
def results_collection_view(request):
    institution = request.user
    student_class = request.GET.get('student_class')
    admission_number = request.GET.get('admission_number')
    students = Student.objects.filter(institution=institution)
    if student_class:
        students = students.filter(student_class=student_class)
    if admission_number:
        students = students.filter(admission_number=admission_number)
    results = Result.objects.filter(student__in=students)

    # Handle score update
    if request.method == 'POST':
        result_id = request.POST.get('result_id')
        new_score = request.POST.get('score')
        if result_id and new_score is not None:
            result = get_object_or_404(Result, id=result_id, student__in=students)
            result.score = new_score
            result.save()
            messages.success(request, f"Score updated for {result.student.name} - {result.subject}")
            return redirect(request.path + f'?student_class={student_class or ""}&admission_number={admission_number or ""}')

    # For dropdown
    class_choices = [
        ('Form 1', 'Form 1'),
        ('Form 2', 'Form 2'),
        ('Form 3', 'Form 3'),
        ('Form 4', 'Form 4'),
    ]
    return render(request, 'results/results_collection.html', {
        'results': results,
        'students': students,
        'class_choices': class_choices,
        'selected_class': student_class,
        'admission_number': admission_number,
    })

@login_required
def update_result(request, result_id):
    result = get_object_or_404(Result, id=result_id, teacher__institution=request.user)
    if request.method == 'POST':
        score = request.POST.get('score')
        if score:
            result.score = score
            result.save()
            messages.success(request, f"✅ Result for {result.student.name} updated!")
        else:
            messages.error(request, "⚠️ Score cannot be empty.")
    return redirect('results_collection')

def add_teacher_view(request):
    if request.method == 'POST':
        form = AddTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save(commit=False)
            teacher.institution = request.user
            raw_password = form.cleaned_data['password']
            teacher.set_password(raw_password)
            teacher.save()
            messages.success(request, "Teacher added successfully.")
            return redirect('dashboard')
    else:
        form = AddTeacherForm()
    return render(request, 'results/add_teacher.html', {'form': form})

def lookup_student(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('teacher_login')
    teacher = get_object_or_404(Teacher, id=teacher_id)
    if request.method == 'POST':
        if 'adm_no' in request.POST:
            adm_no = request.POST['adm_no']
            try:
                student = Student.objects.get(admission_number=adm_no, institution=teacher.institution)
                # Get subjects already entered for this student
                entered_subjects = Result.objects.filter(student=student).values_list('subject', flat=True)
                available_subjects = [s for s in dict(Result._meta.get_field('subject').choices) if s not in entered_subjects]
                if not available_subjects:
                    return render(request, 'results/lookup.html', {
                        'error': 'All subjects have results entered for this student.'
                    })
                form = SingleSubjectResultForm()
                form.fields['subject'].choices = [(s, dict(Result._meta.get_field('subject').choices)[s]) for s in available_subjects]
                return render(request, 'results/enter_results.html', {
                    'student': student,
                    'form': form
                })
            except Student.DoesNotExist:
                return render(request, 'results/lookup.html', {
                    'error': 'Student not found'
                })
        elif 'student_id' in request.POST:
            student = get_object_or_404(Student, id=request.POST.get('student_id'), institution=teacher.institution)
            form = SingleSubjectResultForm(request.POST)
            # Limit subject choices to those not already entered
            entered_subjects = Result.objects.filter(student=student).values_list('subject', flat=True)
            available_subjects = [s for s in dict(Result._meta.get_field('subject').choices) if s not in entered_subjects]
            form.fields['subject'].choices = [(s, dict(Result._meta.get_field('subject').choices)[s]) for s in available_subjects]
            if form.is_valid():
                subject = form.cleaned_data['subject']
                # Double check: prevent duplicate entry
                if Result.objects.filter(student=student, subject=subject).exists():
                    return render(request, 'results/lookup.html', {
                        'error': f'Result for {subject} already entered for this student.'
                    })
                result = form.save(commit=False)
                result.student = student
                result.teacher = teacher
                result.save()
                return render(request, 'results/lookup.html', {
                    'success': f"Result for {dict(Result._meta.get_field('subject').choices)[subject]} saved for {student.name}!"
                })
            return render(request, 'results/enter_results.html', {
                'student': student,
                'form': form
            })
    return render(request, 'results/lookup.html')

def enter_results(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, id=teacher_id) if teacher_id else None
    entered_subjects = Result.objects.filter(student=student).values_list('subject', flat=True)
    available_subjects = [s for s in dict(Result._meta.get_field('subject').choices) if s not in entered_subjects]
    if not available_subjects:
        messages.info(request, 'All subjects have results entered for this student.')
        return redirect('lookup_student')
    if request.method == 'POST':
        form = SingleSubjectResultForm(request.POST)
        form.fields['subject'].choices = [(s, dict(Result._meta.get_field('subject').choices)[s]) for s in available_subjects]
        if form.is_valid():
            subject = form.cleaned_data['subject']
            if Result.objects.filter(student=student, subject=subject).exists():
                messages.error(request, f'Result for {subject} already entered for this student.')
                return redirect('lookup_student')
            result = form.save(commit=False)
            result.student = student
            result.teacher = teacher
            result.save()
            messages.success(request, f'Result for {dict(Result._meta.get_field('subject').choices)[subject]} saved for {student.name}!')
            return redirect('lookup_student')
    else:
        form = SingleSubjectResultForm()
        form.fields['subject'].choices = [(s, dict(Result._meta.get_field('subject').choices)[s]) for s in available_subjects]
    return render(request, 'results/enter_results.html', {'form': form, 'student': student})

class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'results/login.html'
    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'teacher'):
            return reverse('lookup_student')
        else:
            return reverse('dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')