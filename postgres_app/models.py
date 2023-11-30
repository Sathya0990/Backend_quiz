from django.db import models
from django.conf import settings 
from django.contrib.postgres.fields import ArrayField


# Create your models here.

# Courses table to mange information about a course
class courses(models.Model):
    course_id=models.AutoField(primary_key=True)
    course_code=models.IntegerField(unique=True)
    course_name=models.CharField(max_length=50)
    


# Students table to manage the information about a student
class students(models.Model):
    student_id=models.AutoField(primary_key=True,null=False)
    name=models.CharField(max_length=50,null=False)
    courses_list=models.ManyToManyField('courses', blank=True)
    email_id=models.EmailField(unique=True,null=False)
    password=models.CharField(max_length=50,null=False)

# Teachers table to manage the information about a teacher
class teachers(models.Model):    
    teacher_id = models.AutoField(primary_key=True,null=False)
    name = models.CharField(max_length=50,null=False)
    teach_list = models.ManyToManyField('courses', blank=True)
    email_id = models.EmailField(unique=True,null=False)
    password = models.CharField(max_length=50,null=False)


class quizzes(models.Model):

    quiz_id= models.AutoField(primary_key=True) 
    teacher_id=models.ForeignKey(teachers,on_delete=models.CASCADE)
    course_id=models.ForeignKey(courses, on_delete= models.CASCADE)

    quiz_content= ArrayField(

        base_field=models.JSONField(),
        blank=True,
        null=True

    ) 

    start_time=models.CharField(max_length=50)
    start_date=models.CharField(max_length=50)
    duration=models.CharField(max_length=50)


class scores(models.Model):

    student_id=models.ForeignKey(students,on_delete=models.CASCADE)

    course_id=models.ForeignKey(courses, on_delete= models.Model)

    score= models.CharField(max_length=20)

    quiz_attempted = models.BooleanField(default=False)
    attempts_count = models.PositiveIntegerField(default=0)



