# results/forms.py
from django import forms
from .models import Institution, Teacher, Student, Result, StudentResult

class InstitutionForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Institution
        fields = ['name', 'password']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'admission_number', 'student_class']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'admission_number': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'student_class': forms.Select(attrs={'class': 'border rounded p-2 w-full'}),
        }

class LoginForm(forms.Form):
    name = forms.CharField(label='Institution Name', max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Enter institution name',
        'class': 'form-input'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
        'class': 'form-input'
    }))   

class ResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = [
            'mathematics', 'english', 'kiswahili', 'history', 
            'geography', 'cre', 'business', 'agriculture'
        ]
        widgets = {field: forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}) for field in fields}

     

class InstitutionCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = Institution
        fields = ('name',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        institution = super().save(commit=False)
        institution.set_password(self.cleaned_data["password1"])
        if commit:
            institution.save()
        return institution
    
class TeacherLoginForm(forms.Form):
    name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class AddTeacherForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'border rounded p-2 w-full'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'border rounded p-2 w-full'}),
        label="Confirm Password"
    )

    class Meta:
        model = Teacher
        fields = ['name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match")

    def save(self, commit=True):
        teacher = super().save(commit=False)
        teacher.password = self.cleaned_data["password"]
        if commit:
            teacher.save()
        return teacher

class AdmissionLookupForm(forms.Form):
    admission_number = forms.CharField(max_length=20)

class SingleSubjectResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['subject', 'score']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }


