from django.contrib import admin
from django.urls import path,include
from .views import Registration,LoginAPIView,QuizCreateAPIView,FetchCourseID,QuizUpdateAPIView,CourseTeacherAPIView,QuizDeleteAPIView,StudentCourseQuestionsView,StudentQuizAnswerView,ClassStatisticsView,TeacherUpdateQuestionsView

urlpatterns = [

    path("registration/", Registration.as_view(), name='registration'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('teacher/create/', QuizCreateAPIView.as_view(), name='quiz-create'),
    path('update/<int:course_id>/<int:teacher_id>/', QuizUpdateAPIView.as_view(), name='quiz-update'),
    path('delete/<int:course_id>/<int:teacher_id>/', QuizDeleteAPIView.as_view(), name='quiz-delete'),
    path('courses/', CourseTeacherAPIView.as_view(), name='courses'),
    path('course/<str:course_code>/', FetchCourseID.as_view(), name='fetch-course-id'),
    path('student/<int:course_id>/questions/', StudentCourseQuestionsView.as_view(), name='studentquestions'),
    path('student/<course_id>/<student_id>/answers/', StudentQuizAnswerView.as_view(), name='studentanswers'),
    path('teacher/statsview/<course_id>/',ClassStatisticsView.as_view(),name="studentstats"),
    path('teacher/updatehelper/<int:course_id>/<int:teacher_id>/',TeacherUpdateQuestionsView.as_view(),name='updatehelper')
]
