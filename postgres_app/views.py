from django.shortcuts import render
from rest_framework.views import APIView,Response
from .serializers import RegistrationSerializer, LoginSerializer
from .models import students, teachers, quizzes, courses
from rest_framework import status
# Create your views here.


class Registration(APIView):
    
    def get(self,request):
        pass 

    def post(self,request):
        
        serializer=RegistrationSerializer(data=request.data)

        if serializer.is_valid():

            user=serializer.save()

            return Response({"message": "User registered successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email_id']
            password = serializer.validated_data['password']
            is_teacher = serializer.validated_data['is_teacher']

            if is_teacher:
                try:
                    teacher = teachers.objects.get(email_id=email, password=password)
                    teach_list = teacher.teach_list.all()
                    courses_info = []
                    for course in teach_list:
                        quizzes_info = quizzes.objects.filter(teacher_id=teacher, course_id=course)
                        course_info = {
                            'course_name': course.course_name,
                            'quizzes_info': [{
                                'start_date': quiz.start_date,
                                'start_time': quiz.start_time,
                                'duration': quiz.duration
                            } for quiz in quizzes_info]
                        }
                        courses_info.append(course_info)
                    return Response({'courses_info': courses_info}, status=status.HTTP_200_OK)
                except teachers.DoesNotExist:
                    return Response({'error': 'Invalid teacher credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                try:
                    student = students.objects.get(email_id=email, password=password)
                    courses_list = student.courses_list.all()
                    courses_info = []
                    for course in courses_list:
                        teacher_of_course = course.teachers_set.first()  # Fetching teacher for the course
                        quizzes_info = quizzes.objects.filter(teacher_id=teacher_of_course, course_id=course)
                        course_info = {
                            'course_name': course.course_name,
                            'quizzes_info': [{
                                'start_date': quiz.start_date,
                                'start_time': quiz.start_time,
                                'duration': quiz.duration
                            } for quiz in quizzes_info]
                        }
                        courses_info.append(course_info)
                    return Response({'courses_info': courses_info}, status=status.HTTP_200_OK)
                except students.DoesNotExist:
                    return Response({'error': 'Invalid student credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

