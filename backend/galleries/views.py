from django.shortcuts import render,get_object_or_404, get_list_or_404
from .serializers import CardSerializer, CardBodySerializer, ImageSerializer
from django.core import serializers
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import Card
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
import os
from drf_yasg import openapi
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
# from django.utils.decorators import method_decorator
# from rest_framework.decorators import action
# https://drf-yasg.readthedocs.io/en/stable/custom_spec.html


# Create your views here.


sessionkey = openapi.Parameter('sessionkey', openapi.IN_HEADER, description="sessionkey", type=openapi.TYPE_STRING)



def session_check(sessionkey):
    session = Session.objects.filter(session_key=sessionkey)
    if session:
        date = timezone.now()
        if date > session[0].expire_date:
            sessionstatus = False
            # session[0].delete()
        else:
            sessionstatus = True
    else:
        sessionstatus = False

    return sessionstatus




class GalleryViewSet(viewsets.ModelViewSet):
    serializer_class = Card
    parser_classes = (MultiPartParser,)
    @swagger_auto_schema(
        manual_parameters=[sessionkey],
    )  
    def get(self, request, type, no):
        sessionkey = request.headers.get('sessionkey')
        sessionstatus = session_check(sessionkey)
        if sessionstatus:
            card = Card.objects.filter(sessionkey=sessionkey)
            imagefield = str(type) + '_image_' + str(no)
            cardquery = list(card.values(imagefield))
            imagefile = cardquery[0][imagefield]
            base_address = 'C:/Users/multicampus/Desktop/s04p23c106/backend/pjt/media'
            img = open(os.path.join(base_address, imagefile), 'rb')
            response = FileResponse(img)
            response['sessionkey'] = sessionkey
            return response
        else:
            return JsonResponse({'status': 'session이 존재하지 않거나 유효하지 않습니다.'})


    @swagger_auto_schema(
        request_body=ImageSerializer,
        manual_parameters=[sessionkey],
        ) 
    def create(self, request, type, no, **kwargs):
        sessionkey = request.headers.get('sessionkey')
        sessionstatus = session_check(sessionkey)
        image = request.data.get('image')
        if sessionstatus:
            card = get_object_or_404(Card, sessionkey=sessionkey)
            imagefield = str(type) + '_image_' + str(no)
            data = {imagefield: image}
            serializer = CardSerializer(card, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.sessionkey = sessionkey
                serializer.save()
                return JsonResponse(serializer.data)
        else:
            return JsonResponse({'status': 'session이 존재하지 않거나 유효하지 않습니다.'})


@swagger_auto_schema(
        method='get',
        manual_parameters=[sessionkey],
    ) 
@api_view(['get'])
def passcard(request):
    
    sessionkey = request.headers.get('sessionkey')
    sessionstatus = session_check(sessionkey)
    if sessionstatus:
        card = get_object_or_404(Card, sessionkey=sessionkey)
        serializer = CardSerializer(card)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'status': 'session이 존재하지 않거나 유효하지 않습니다.'})





        

# @swagger_auto_schema(
#         methods=['post','put'],
#         parser_classes=(MultiPartParser,),
#         request_body=no_body,
#         manual_parameters=[sessionkey, input1, input2, input3, input4, output1, output2, output3, output4],
#     ) 
# @api_view(['POST', 'PUT'])
# def receiveimage(request):
#     sessionkey = request.headers.get('sessionkey')
#     if Card.objects.filter(sessionkey=sessionkey):
#         card = get_object_or_404(Card, sessionkey=sessionkey)
#         serializer = CardSerializer(card, data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save(sessionkey=sessionkey)
#             return JsonResponse(serializer.data)
#     else:
#         serializer = CardSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save(sessionkey=sessionkey)
#             return JsonResponse(serializer.data)
#     return HttpResponse({'hi'})


# @swagger_auto_schema(
#         method='get',
#         body_serializer=CardBodySerializer,
#         manual_parameters=[sessionkey],
#     )  
# @api_view(['get'])
# def giveimage(request, input_no):
#     sessionkey = request.headers.get('sessionkey')
#     if Card.objects.filter(sessionkey=sessionkey):
#         card = Card.objects.filter(sessionkey=sessionkey)
#         imagefield = 'input_image_' + str(input_no)
#         cardquery = list(card.values(imagefield))
#         # cardquery[0]['sessionkey'] = sessionkey
#         imagefile = cardquery[0][imagefield]
#         base_address = 'C:/Users/multicampus/Desktop/s04p23c106/backend/pjt/media'
#         img = open(os.path.join(base_address, imagefile), 'rb')
#         response = FileResponse(img)
#         response['sessionkey'] = sessionkey
#         return response
#         # return FileResponse(img)
#         # return JsonResponse(response[0])
#     else:
#         return JsonResponse({'status': 'session이 존재하지 않습니다.'})

