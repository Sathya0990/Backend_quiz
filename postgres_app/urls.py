from django.contrib import admin
from django.urls import path,include
from .views import Registration,LoginAPIView,QuizCreateAPIView,FetchCourseID,QuizUpdateAPIView

urlpatterns = [

    path("registration/", Registration.as_view(), name='registration'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('teacher/create/', QuizCreateAPIView.as_view(), name='quiz-create'),
    path('course/<str:course_code>/', FetchCourseID.as_view(), name='fetch-course-id'),
    path('update/<int:quiz_id>/', QuizUpdateAPIView.as_view(), name='quiz-update'),



]
