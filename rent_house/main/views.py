from rest_framework import generics
from .models import House
from .serializers import HouseSerializer
from django.shortcuts import render
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from .auth import generate_access_token, generate_refresh_token
from django.views.decorators.csrf import csrf_protect
import jwt
from django.conf import settings
# views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import House, Booking
from .serializers import BookingSerializer


class CreateBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        house_id = request.data.get('house')
        house = House.objects.get(id=house_id)

        if house.is_booked:
            return Response({'detail': 'House is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        house.is_booked = True
        house.save()

        return super().create(request, *args, **kwargs)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': user.username,
                'email': user.email
            }
        })


@api_view(['GET'])
def user(request):
    user = request.user
    serialized_user = UserSerializer(user).data
    return Response({'user': serialized_user})


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'username and password required')

    user = User.objects.filter(username=username).first()
    if (user is None):
        raise exceptions.AuthenticationFailed('user not found')
    if (not user.check_password(password)):
        raise exceptions.AuthenticationFailed('wrong password')

    serialized_user = UserSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'user': serialized_user,
    }

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh_token_view(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')

    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = generate_access_token(user)
    return Response({'access_token': access_token})


class HouseListCreate(generics.ListCreateAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = House.objects.filter(is_booked=False)
        min_floor = self.request.query_params.get('min_floor', None)
        max_floor = self.request.query_params.get('max_floor', None)
        min_rooms = self.request.query_params.get('min_rooms', None)
        max_rooms = self.request.query_params.get('max_rooms', None)

        if min_floor is not None:
            queryset = queryset.filter(floor__gte=min_floor)
        if max_floor is not None:
            queryset = queryset.filter(floor__lte=max_floor)
        if min_rooms is not None:
            queryset = queryset.filter(rooms__gte=min_rooms)
        if max_rooms is not None:
            queryset = queryset.filter(rooms__lte=max_rooms)

        return queryset

