from django.shortcuts import render

# Create your views here.
# results/views.py
from django.shortcuts import render, redirect
from .models import Subject, Exam, Result
from accounts.models import Student
from django.contrib.auth.decorators import login_required

@login_required
def marks_entry(request):
    if request.method == 'POST':
        student_id = request.POST['student']
        subject_id = request.POST['subject']
        exam_id = request.POST['exam']
        marks = request.POST['marks']
        Result.objects.create(
            student_id=student_id,
            subject_id=subject_id,
            exam_id=exam_id,
            marks=marks
        )
        return redirect('marks_entry')
    students = Student.objects.all()
    subjects = Subject.objects.all()
    exams = Exam.objects.all()
    return render(request, 'results/marks_entry.html', {
        'students': students,
        'subjects': subjects,
        'exams': exams
    })
@login_required
def view_results(request):
    student = request.user.student
    results = Result.objects.filter(student=student)
    return render(request, 'results/view_results.html', {'results': results})
