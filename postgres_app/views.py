from django.shortcuts import render
from rest_framework.views import APIView,Response
from .serializers import RegistrationSerializer, LoginSerializer, QuizCreateSerializer,CourseTeacherSerializer
from .models import students, teachers, quizzes, courses
from rest_framework import status
import json 
from django.shortcuts import get_object_or_404


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

# class QuizCreateAPIView(APIView):
#     def post(self, request):
#         teacher_id = request.data.get('teacher_id')
#         teacher_courses = teachers.objects.get(teacher_id=teacher_id).teach_list.all()
        
#         print(teacher_courses)
#         course_id = request.data.get('course_id')
        
#         if int(course_id) not in [course.course_id for course in teacher_courses]:
#             return Response({'message': 'Teacher not authorized for this course'}, status=status.HTTP_403_FORBIDDEN)
        
#         serializer = QuizCreateSerializer(data=request.data)
#         if serializer.is_valid():
            
#             quiz_content = serializer.validated_data['quiz_content']
#             if len(quiz_content) < 10:
#                 return Response({'error': 'Number of questions should be at least 10.'}, status=status.HTTP_400_BAD_REQUEST)
#             serializer.save()
#             return Response({'message': 'Quiz created successfully'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class QuizCreateAPIView(APIView):

#     def post(self, request):
#         teacher_id = request.data.get('teacher_id')
#         teacher = teachers.objects.get(teacher_id=teacher_id)
#         teacher_courses = teacher.teach_list.all()
        
        
#         print(f"Teacher's courses: {[course.course_id for course in teacher_courses]}")
        
#         course_id = request.data.get('course_id')
#         print(f"Requested course ID: {course_id}")
        

#         if course_id not in [course.course_id for course in teacher_courses]:
#             return Response({'message': 'Teacher not authorized for this course'}, status=status.HTTP_403_FORBIDDEN)
        
#         serializer = QuizCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             quiz_content = serializer.validated_data['quiz_content']
#             # if len(quiz_content) < 10:
#             #     return Response({'error': 'Number of questions should be at least 10.'}, status=status.HTTP_400_BAD_REQUEST)
#             serializer.save()
#             return Response({'message': 'Quiz created successfully'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizCreateAPIView(APIView):
    def post(self, request):
        teacher_id = request.data.get('teacher_id')
        course_id = request.data.get('course_id')

        # Check if a quiz already exists for the provided course and teacher
        existing_quiz = quizzes.objects.filter(teacher_id=teacher_id, course_id=course_id).first()
        if existing_quiz:
            return Response({'message': 'Quiz for this course already exists'}, status=status.HTTP_403_FORBIDDEN)

        # Fetching the teacher's courses for authorization
        teacher = get_object_or_404(teachers, teacher_id=teacher_id)
        teacher_courses = teacher.teach_list.all()

        print(f"Teacher's courses: {[course.course_id for course in teacher_courses]}")
        print(f"Requested course ID: {course_id}")

        # Authorization check - Ensure the teacher is authorized for the requested course
        if course_id not in [course.course_id for course in teacher_courses]:
            return Response({'message': 'Teacher not authorized for this course'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = QuizCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure minimum number of questions, if required
            quiz_content = serializer.validated_data['quiz_content']

            # FOR TESTING COMMENTED THE BELOW, FOR PROD, UNCOMMENT!!

            # if len(quiz_content) < 10:
            #     return Response({'error': 'Number of questions should be at least 10.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({'message': 'Quiz created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class FetchCourseID(APIView):
    def get(self, request, course_code):
        try:
            course = courses.objects.get(course_code=course_code)
            return Response({'course_id': course.course_id}, status=status.HTTP_200_OK)
        except courses.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        

class QuizUpdateAPIView(APIView):
    def put(self, request, course_id):
        # Get the existing quiz instance or return a 404 if it doesn't exist
        quiz = get_object_or_404(quizzes, course_id=course_id)

        # Ensure that only the teacher who created the quiz can modify it
        teacher_id = request.data.get('teacher_id')
        if quiz.teacher_id.teacher_id != teacher_id:
            return Response({'message': 'Unauthorized to modify this quiz'}, status=status.HTTP_403_FORBIDDEN)

        # Serialize the updated data and apply changes to the quiz instance
        serializer = QuizCreateSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Quiz updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseTeacherAPIView(APIView):
    def get(self, request):
        course_teacher_info = courses.objects.select_related('teachers').values(
            'course_code',
            'course_id',
            'course_name',
            'teachers__name',
            'teachers__teacher_id'
        )
        
        return Response(course_teacher_info)