from django.shortcuts import render
from rest_framework.views import APIView,Response
from .serializers import RegistrationSerializer, LoginSerializer, QuizCreateSerializer,CourseTeacherSerializer,studentserializer
from .models import students, teachers, quizzes, courses, scores
from rest_framework import status
import json 
from django.shortcuts import get_object_or_404
from django.db.models import Max, Min
from statistics import mean, median, mode
from decimal import Decimal




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

            try:
                if is_teacher:
                    # Fetching teacher data
                    teacher = teachers.objects.get(email_id=email, password=password)
                    teach_list = teacher.teach_list.all()

                    teacher_info = {
                        'teacher_id': teacher.teacher_id,
                        'name': teacher.name,
                        'email_id': teacher.email_id
                    }
                    courses_info = []

                    for course in teach_list:
                        quizzes_info = quizzes.objects.filter(teacher_id=teacher, course_id=course)
                        course_info = {
                            'course_code': course.course_code,
                            'course_id': course.course_id,
                            'course_name': course.course_name,
                            'quizzes_info': [{
                                'start_date': quiz.start_date,
                                'start_time': quiz.start_time,
                                'duration': quiz.duration
                            } for quiz in quizzes_info]
                        }
                        courses_info.append(course_info)

                    return Response({'teacher_info': teacher_info, 'courses_info': courses_info}, status=status.HTTP_200_OK)
                else:
                    # Fetching student data
                    student = students.objects.get(email_id=email, password=password)
                    student_info = {
                        'student_id': student.student_id,
                        'name': student.name,
                        'email_id': student.email_id
                    }
                    courses_list = student.courses_list.all()
                    courses_info = []

                    for course in courses_list:
                        teacher_of_course = course.teachers_set.first()
                        quizzes_info = quizzes.objects.filter(teacher_id=teacher_of_course, course_id=course)
                        quiz_info_list = [{
                            'start_date': quiz.start_date,
                            'start_time': quiz.start_time,
                            'duration': quiz.duration
                        } for quiz in quizzes_info]

                        course_info = {
                            'course_code': course.course_code,
                            'course_id': course.course_id,
                            'course_name': course.course_name,
                            'quizzes_info': quiz_info_list
                        }
                        courses_info.append(course_info)

                    # Fetching scores for the student
                    all_scores = scores.objects.filter(student_id=student)
                    scores_info = [{
                        'course_id': score.course_id.course_id,
                        'quiz_attempted': score.quiz_attempted,
                        'attempts_count': score.attempts_count,
                        'score': score.score
                    } for score in all_scores]

                    return Response({'student_info': student_info, 'courses_info': courses_info, 'scores_info': scores_info}, status=status.HTTP_200_OK)

            except teachers.DoesNotExist:
                return Response({'error': 'Invalid teacher credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            except students.DoesNotExist:
                return Response({'error': 'Invalid student credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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




class QuizUpdateAPIView(APIView):
    def put(self, request, course_id,teacher_id):
        # Get the existing quiz instance or return a 404 if it doesn't exist
        quiz = get_object_or_404(quizzes, course_id=course_id,teacher_id=teacher_id)

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


class QuizDeleteAPIView(APIView):
    def delete(self, request, course_id,teacher_id):
        # Get the quiz instance or return a 404 if it doesn't exist
        try:
            quiz = quizzes.objects.get(course_id=course_id,teacher_id=teacher_id)
        except quizzes.DoesNotExist:
            return Response({'message': 'Quiz does not exists'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that only the teacher who created the quiz can delete it
        # teacher_id = request.data.get('teacher_id')
        print(teacher_id, quiz.teacher_id.teacher_id)
        if quiz.teacher_id.teacher_id != teacher_id:
            return Response({'message': 'Unauthorized to delete this quiz'}, status=status.HTTP_403_FORBIDDEN)

        # Delete the quiz
        quiz.delete()

        teacher = teachers.objects.get(teacher_id=teacher_id)
        teach_list = teacher.teach_list.all()
        # print(teacher)
        teacher_info={
        'teacher_id':teacher.teacher_id,
        'name':teacher.name,
        'email_id':teacher.email_id
        }
        courses_info = []
        for course in teach_list:
            quizzes_info = quizzes.objects.filter(teacher_id=teacher, course_id=course)
            course_info = {
                'course_code':course.course_id,
                'course_id':course.course_id,
                'course_name': course.course_name,
                'quizzes_info': [{
                    'start_date': quiz.start_date,
                    'start_time': quiz.start_time,
                    'duration': quiz.duration
                } for quiz in quizzes_info]
            }
            courses_info.append(course_info)
        return Response({'message': 'Quiz deleted successfully','teacher_info':teacher_info,'courses_info': courses_info}, status=status.HTTP_204_NO_CONTENT)
        

        # return Response({}, status=status.)




class FetchCourseID(APIView):
    def get(self, request, course_code):
        try:
            course = courses.objects.get(course_code=course_code)
            return Response({'course_id': course.course_id}, status=status.HTTP_200_OK)
        except courses.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        


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


class StudentCourseQuestionsView(APIView):
    def get(self, request, course_id):
        try:
            course = courses.objects.get(pk=course_id)
            quizzes_for_course = quizzes.objects.filter(course_id=course)
            
            questions = []
            for quiz in quizzes_for_course:

                quiz_questions=quiz.quiz_content
                for q in quiz_questions:
                # Exclude correct answer
                    q.pop('correct_answer', None)  
                    questions.append(q)
                # questions.extend(quiz.quiz_content)  
            
            

            return Response({'questions': questions})
        except courses.DoesNotExist:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        


class TeacherUpdateQuestionsView(APIView):
    def get(self, request, course_id,teacher_id):
        try:
            course = courses.objects.get(pk=course_id)
            quizzes_for_course = quizzes.objects.filter(course_id=course,teacher_id=teacher_id)
            
            questions = []
            for quiz in quizzes_for_course:

            #     quiz_questions=quiz.quiz_content
            #     for q in quiz_questions:
            #     # Exclude correct answer
            #         q.pop('correct_answer', None)  
            #         questions.append(q)
                questions.extend(quiz.quiz_content)  
            
            
            return Response({'questions': questions})
        except courses.DoesNotExist:
            return Response({"message": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        



class StudentQuizAnswerView(APIView):
    def post(self, request, course_id, student_id):
        try:
            student = students.objects.get(student_id=student_id)
            quiz = quizzes.objects.get(course_id=course_id)
            quiz_questions = quiz.quiz_content
            user_responses = request.data['answers']
            
            total_questions = len(quiz_questions)
            correct_answers = 0
            
            for user_response in user_responses:
                question = user_response['question']
                
                if isinstance(user_response,list):
                    chosen_option = set(user_response['chosen_option'])
                else:
                    chosen_option=user_response['chosen_option']
                
                # print(chosen_option)

                # for quiz_question in quiz_questions:
                #     if quiz_question['question'] == question:
                #         if isinstance(correct_options,list):
                #             correct_options = set(quiz_question['correct_answer'])
                #         else:
                #              correct_options = quiz_question['correct_answer']
                #         print(correct_options)
                #     # Partial grading for multiple-answer questions
                #         if chosen_option.issuperset(correct_options):  
                #             correct_answers += 1 / len(correct_options)  
                #         break

                for quiz_question in quiz_questions:
                    if quiz_question['question'] == question:
                        correct_answer = quiz_question['correct_answer']
                        
                        # print(type(correct_answer), type(chosen_option), type(chosen_option)!=type(correct_answer), chosen_option,correct_answer)
                        # print(correct_answer)
                        # Handling single-answer and multiple-answer questions differently
                        if  type(correct_answer)!=type(chosen_option) or isinstance(chosen_option, list):
                        
                            if type(correct_answer)!=type(chosen_option):
                                if chosen_option in correct_answer:
                                    correct_answers += 1 / len(correct_answer)
                            else:
                                for option in chosen_option:
                                    if option in correct_answer:
                                        correct_answers += 1 / len(correct_answer)
                                    # print(chosen_option,correct_answer)
                        else:
                            if chosen_option == correct_answer:
                                correct_answers += 1
                        
                        break



            final_score_percentage = (correct_answers / total_questions) * 100
            final_score = f"{correct_answers}/{total_questions}"
            
            # Storing in scores table
            # scores.objects.create(student_id=student, course_id=quiz.course_id, score=correct_answers)
            

            existing_score = scores.objects.filter(student_id=student, course_id=quiz.course_id).first()
            if existing_score:
                existing_score.quiz_attempted = True
                existing_score.attempts_count += 1  # Increment attempts count
                existing_score.save()
            else:
                # If no existing score, create a new entry and mark the quiz as attempted
                scores.objects.create(
                    student_id=student,
                    course_id=quiz.course_id,
                    score=correct_answers,
                    quiz_attempted=True,
                    attempts_count=1  # Set attempts count as 1 for the first attempt
                )
            all_scores = scores.objects.filter(student_id=student, course_id=quiz.course_id)

            # Prepare a list of score information
            scores_info = []
            for score in all_scores:
                scores_info.append({
                    'score_id': score.id,
                    'quiz_attempted': score.quiz_attempted,
                    'attempts_count': score.attempts_count,
                    'score': score.score
                    # Include other relevant score information here
                })
  

            return Response(
                {
                    'percentage': final_score_percentage,
                    'final_score': final_score,
                    'correct_answers': correct_answers,
                    'total_questions': total_questions,
                    'scores_info': scores_info
                }, 
                status=status.HTTP_200_OK
            )
        
        except students.DoesNotExist:
            return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        except quizzes.DoesNotExist:
            return Response({"message": "Quiz not found for this course"}, status=status.HTTP_404_NOT_FOUND) 

class ClassStatisticsView(APIView):
    def get(self, request, course_id):
        try:
            quiz = quizzes.objects.get(course_id=course_id)
            scores_data = scores.objects.filter(course_id=course_id)

            no_of_students_registered = students.objects.filter(courses_list=quiz.course_id).count()
            no_of_students_attempted_quiz = scores_data.count()
            no_of_students_left = no_of_students_registered - no_of_students_attempted_quiz

            # Convert score strings to Decimal type for statistical calculations
            all_scores = [Decimal(score.score) for score in scores_data]
            mean_score = mean(all_scores)
            median_score = median(all_scores)
            mode_score = mode(all_scores)

            # Retrieve top and bottom scores
            top_scores = scores_data.order_by('-score')[:5]
            bottom_scores = scores_data.order_by('score')[:5]

            class_stats = {
                "no_of_students_registered": no_of_students_registered,
                "no_of_students_attempted_quiz": no_of_students_attempted_quiz,
                "no_of_students_left": no_of_students_left,
                "mean_score": mean_score,
                "median_score": median_score,
                "mode_score": mode_score,
                "top_5_scores": [
                    {
                        "score_id": score.id,
                        "student_id": score.student_id.student_id,
                        "score": score.score
                    }
                    for score in top_scores
                ],
                "bottom_5_scores": [
                    {
                        "score_id": score.id,
                        "student_id": score.student_id.student_id,
                        "score": score.score
                    }
                    for score in bottom_scores
                ]
            }

            return Response(class_stats, status=status.HTTP_200_OK)
        
        except quizzes.DoesNotExist:
            return Response({"message": "Quiz not found for this course"}, status=status.HTTP_404_NOT_FOUND)
