
from rest_framework import serializers
from .models import students, teachers, courses

class RegistrationSerializer(serializers.Serializer):
    
    name = serializers.CharField()
    email_id = serializers.EmailField()
    password = serializers.CharField()
    is_teacher = serializers.BooleanField()
    courses_list = serializers.JSONField()

    def create(self, validated_data):

        if validated_data['is_teacher']:
            teacher = teachers.objects.create(
                name=validated_data['name'],
                email_id=validated_data['email_id'],
                password=validated_data['password']
            )
            self._handle_courses(teacher, validated_data['courses_list'], is_teacher=True)
            return teacher
        
        else:
            student = students.objects.create(
                name=validated_data['name'],
                email_id=validated_data['email_id'],
                password=validated_data['password']
            )
            self._handle_courses(student, validated_data['courses_list'], is_teacher=False)
            return student

    def _handle_courses(self, user, courses_list, is_teacher=False):
        for course_data in courses_list:
            course_code = course_data.get('course_code')
            course_name = course_data.get('course_name')
            teacher_id = course_data.get('teacher_id')

            if is_teacher:
                if not (course_code and course_name):
                    raise serializers.ValidationError({"error": "Course code and name are required for teachers."})

                new_course, _ = courses.objects.get_or_create(
                    course_code=course_code,
                    defaults={'course_name': course_name}
                )
                user.teach_list.add(new_course)
            else:
                if not (course_code and teacher_id):
                    raise serializers.ValidationError({"error": "Course code and teacher ID are required for students."})

                if not teachers.objects.filter(teacher_id=teacher_id).exists():
                    raise serializers.ValidationError({
                        "error": f"Teacher with ID {teacher_id} does not exist. Add later"
                    })

                # Fetch existing courses for students without creating new ones
                existing_course = courses.objects.filter(course_code=course_code)
                if existing_course.exists():
                    user.courses_list.add(existing_course.first())
