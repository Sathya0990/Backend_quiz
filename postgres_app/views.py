from django.shortcuts import render
from rest_framework.views import APIView,Response
from .serializers import RegistrationSerializer
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


