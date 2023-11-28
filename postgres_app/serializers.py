from rest_framework import serializers
from .models import students, teachers, courses, quizzes

class RegistrationSerializer(serializers.Serializer):
    
    name = serializers.CharField()
    email_id = serializers.EmailField()
    password = serializers.CharField()
    is_teacher = serializers.BooleanField()
    courses_list = serializers.JSONField()

    def create(self, validated_data):
        error_messages = []

        if validated_data['is_teacher']:
            teacher = teachers.objects.create(
                name=validated_data['name'],
                email_id=validated_data['email_id'],
                password=validated_data['password']
            )
            self._handle_courses(teacher, validated_data['courses_list'], is_teacher=True, errors=error_messages)
            return teacher if not error_messages else error_messages
        
        else:
            student = students.objects.create(
                name=validated_data['name'],
                email_id=validated_data['email_id'],
                password=validated_data['password']
            )
            self._handle_courses(student, validated_data['courses_list'], is_teacher=False, errors=error_messages)
            return student if not error_messages else error_messages

    def _handle_courses(self, user, courses_list, is_teacher=False, errors=[]):
        for course_data in courses_list:
            course_code = course_data.get('course_code')
            course_name = course_data.get('course_name')
            teacher_id = course_data.get('teacher_id')

            if is_teacher:
                if not (course_code and course_name):
                    errors.append({"error": "Course code and name are required for teachers."})
                    return

                new_course, _ = courses.objects.get_or_create(
                    course_code=course_code,
                    defaults={'course_name': course_name}
                )
                user.teach_list.add(new_course)
            else:
                if not (course_code and teacher_id):
                    errors.append({"error": "Course code and teacher ID are required for students."})
                    return

                if not teachers.objects.filter(teacher_id=teacher_id).exists():
                    errors.append({
                        "error": f"Teacher with ID {teacher_id} does not exist. Add later"
                    })
                    return

                # Fetch existing courses for students without creating new ones
                existing_course = courses.objects.filter(course_code=course_code)
                if existing_course.exists():
                    user.courses_list.add(existing_course.first())

class LoginSerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    password = serializers.CharField()
    is_teacher = serializers.BooleanField(default=False)

class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = quizzes
        fields = ['teacher_id', 'course_id', 'quiz_content', 'start_time', 'start_date', 'duration']



class CourseTeacherSerializer(serializers.ModelSerializer):
    course_code = serializers.IntegerField(source='course_code')
    course_name = serializers.CharField(source='course_name')
    teacher_name = serializers.CharField(source='teacher.name')
    teacher_id = serializers.IntegerField(source='teacher.teacher_id')

    class Meta:
        model = courses
        fields = ['course_code', 'course_name', 'teacher_name', 'teacher_id']
