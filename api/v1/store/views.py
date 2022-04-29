import json
import random
import string

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from authentication.models import CasperUser
from common.models import Address, NetworkResponse
from common.utils import Validators, JwtToken, CasperMail
from common.literals import *
from store.models import *
from store.serializers import *


# ----------------------------------@mit----------------------------------
# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_store(request):
    try:
        # extract user from request
        user = request.user

        if user.is_casper_admin and user.is_active:
            store_id = request.GET.get('store_id', None)
            if store_id is None:
                return JsonResponse(
                    NetworkResponse(status='STORE_ID_PARAMETER_MISSING', message=STORE_ID_PARAMETER_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            store = Store.objects.get(id=store_id)
            serializer = StoreSerializer(store)
            return JsonResponse(
                NetworkResponse(status='STORE_RETRIEVED', message=STORE_RETRIEVED, data=serializer.data).as_dict,
                status=status.HTTP_200_OK)

        # get staff instance from the user (reverse relationship)
        staff = user.store_staff if (user.is_staff and user.is_active) else None

        # If staff is not None, then the user is a store staff
        if staff:
            store = staff.store
            return JsonResponse(
                NetworkResponse(status='STORE_RETRIEVED', message=STORE_RETRIEVED, data=store.as_dict).as_dict,
                status=status.HTTP_200_OK)
        else:
            # If staff is None, then the user is not authorized to access this endpoint
            return JsonResponse(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                                status=status.HTTP_401_UNAUTHORIZED)
    # If any exception occurs, return an error response
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_stores(request):
    try:
        # extract user from request
        user = request.user

        if user.is_casper_admin and user.is_active:
            stores = Store.objects.all()
            serializer = StoreSerializer(stores, many=True)
            return JsonResponse(
                NetworkResponse(status='STORES_RETRIEVED', message=STORES_RETRIEVED, data=serializer.data).as_dict,
                status=status.HTTP_200_OK)
        elif not user.is_active:
            return JsonResponse(NetworkResponse(status='ACCOUNT_INACTIVE', message=ACCOUNT_INACTIVE).as_dict,
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            # If user is not a casper admin, then the user is not authorized to access this endpoint
            return JsonResponse(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                                status=status.HTTP_401_UNAUTHORIZED)
    # If any exception occurs, return an error response
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# View to register a new store
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def register_store(request):
    try:
        # extract user from request
        requested_user = request.user

        # Only Casper Admin can register a store
        # So, checking if the user is a casper admin and is active
        if requested_user.is_casper_admin and requested_user.is_active:

            # extract store data from request
            store_data = json.loads(request.body)
            user_data = store_data.pop('user')

            # If email is not provided
            if not store_data.get('email'):
                return JsonResponse(NetworkResponse(status='EMAIL_REQUIRED', message=EMAIL_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if phone is not provided
            if not store_data.get('phone'):
                return JsonResponse(NetworkResponse(status='PHONE_REQUIRED', message=PHONE_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if gstin is not provided
            if not store_data.get('gstin'):
                return JsonResponse(NetworkResponse(status='GSTIN_REQUIRED', message=GSTIN_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if email is not valid
            if Validators.validate_email(store_data.get('email')) is False or Validators.validate_email(
                    user_data.get('email')) is False:
                return JsonResponse(NetworkResponse(status='EMAIL_INVALID', message=EMAIL_INVALID).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if phone is not valid
            if Validators.validate_phone_number(store_data.get('phone')) is False or Validators.validate_phone_number(
                    user_data.get('phone')) is False:
                return JsonResponse(NetworkResponse(status='PHONE_INVALID', message=PHONE_INVALID).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if store email is already registered
            if Validators.is_email_exists(email=store_data.get('email'), model=Store) is True:
                return JsonResponse(
                    NetworkResponse(status='EMAIL_ALREADY_EXISTS', message=EMAIL_ALREADY_EXISTS).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if store phone is already registered
            if Validators.is_phone_exists(phone=store_data.get('phone'), model=Store) is True:
                return JsonResponse(
                    NetworkResponse(status='PHONE_ALREADY_EXISTS', message=PHONE_ALREADY_EXISTS).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if gstin is already registered
            if Validators.is_gstin_exists(gstin=store_data.get('gstin'), model=Store) is True:
                return JsonResponse(
                    NetworkResponse(status='GSTIN_ALREADY_EXISTS', message=GSTIN_ALREADY_EXISTS).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # If user email is already registered
            if Validators.is_email_exists(email=user_data.get('email'), model=CasperUser) is True:
                return JsonResponse(
                    NetworkResponse(status='USER_EMAIL_ALREADY_EXISTS', message=USER_EMAIL_ALREADY_EXISTS).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # If user phone is already registered
            if Validators.is_phone_exists(phone=user_data.get('phone'), model=CasperUser) is True:
                return JsonResponse(
                    NetworkResponse(status='USER_PHONE_ALREADY_EXISTS', message=USER_PHONE_ALREADY_EXISTS).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # Extracting user email and first name
            first_name = user_data.pop('first_name')
            email = user_data.pop('email')

            # If first name is not provided
            if not first_name:
                return JsonResponse(NetworkResponse(status='FIRST_NAME_REQUIRED', message=FIRST_NAME_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # Finally, adding data to the store
            address = store_data.pop('address')
            store_data['address'] = Address.objects.create(**address)
            store_data['category'] = StoreCategory.objects.get(id=store_data['category'])
            store = Store(**store_data)
            store.is_active = True
            store.save()

            # Generating temporary password
            temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

            # Adding user to the database
            user_data['is_staff'] = True
            user_data['is_store_admin'] = True
            user_data['is_active'] = True
            user = CasperUser.objects.create_user(email=email, password=temp_password, first_name=first_name,
                                                  **user_data)

            # Adding staff to the store
            staff = StoreStaff(store=store, user=user)
            staff.position = 'Admin'
            staff.save()

            # Creating Staff Permissions
            permissions = StaffPermission(staff=staff, manage_catalogues=True, manage_stores=True, manage_vendors=True,
                                          manage_customers=True, manage_orders=True, manage_reports=True,
                                          manage_staffs=True, manage_settings=True)
            permissions.save()

            # sending the temp password with email
            text_content = f'Hey {first_name}, Welcome to Casper POS. Use this temporary password -  {temp_password} to access your admin panel.'
            html_content = f'''<div style = "font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2" >
                                                        <div style="margin:50px auto;width:70%;padding:20px 0">
                                                            <div style="border-bottom:1px solid #eee">
                                                            <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Casper India</a>
                                                            </div>
                                                            <p style="font-size:1.1em">Hey {first_name},</p>
                                                            <p>Welcome to Casper POS. Your store store is successfully registered with our POS system. To access your POS dashboard use the below temporary password. </p>
                                                            <h3 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{temp_password}</h3>
                                                            <p style="font-size:0.9em;">Regards,<br />Rajan, Casper India</p>
                                                            <hr style="border:none;border-top:1px solid #eee" />
                                                            <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                                                            <p>Casper Technology Services Pvt. Ltd.</p>
                                                            <p>353 & 354 - 2nd Floor, Ideabox Coworking Varthur Rd,</p>
                                                            <p>Aswath Nagar, Flyover, before, Kundalahalli, Marathahalli, </p>
                                                            <p>Bengaluru, Karnataka 560037</p>
                                                            </div>
                                                        </div>
                                                    </div>'''
            CasperMail.send_multi_alternative_email(
                subject=f'Welcome to Casper POS System',
                text_content=text_content,
                html_content=html_content,
                to=email)

            # Finally, sending the response
            network_response = NetworkResponse(status='STORE_ADDED', message=STORE_ADDED, data=store.as_dict)
            return JsonResponse(network_response.as_dict, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                                status=status.HTTP_401_UNAUTHORIZED)
    except StoreCategory.DoesNotExist:
        return JsonResponse(
            NetworkResponse(status='STORE_CATEGORY_NOT_FOUND', message=STORE_CATEGORY_NOT_FOUND).as_dict,
            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse(
            NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# View to add a new store staff
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_staff(request):
    try:
        # extracting user from the token
        user = request.user

        # if user is active and is a store admin
        if user.is_staff and user.is_active and user.is_store_admin:

            # getting the instance of the admin from the user (reverse relationship)
            store_admin = user.store_staff

            # if the store admin has staff permission
            if store_admin.permission.has_staff_permissions:

                # getting the store from the store admin
                store = store_admin.store

                # getting the data from the request
                staff_data = request.data

                # popup the email from the request
                email = staff_data.pop('email') if 'email' in staff_data else None

                # if the email is not provided
                if not email:
                    return JsonResponse(NetworkResponse(status='EMAIL_REQUIRED', message=EMAIL_REQUIRED).as_dict,
                                        status=status.HTTP_400_BAD_REQUEST)

                # if the email is not valid
                if Validators.validate_email(email) is False:
                    return JsonResponse(NetworkResponse(status='EMAIL_INVALID', message=EMAIL_INVALID).as_dict,
                                        status=status.HTTP_400_BAD_REQUEST)

                # popup the first name, position and permission from the request
                first_name = staff_data.pop('first_name') if 'first_name' in staff_data else None
                position = staff_data.pop('position') if 'position' in staff_data else None
                permissions = staff_data.pop('permissions') if 'permissions' in staff_data else None

                # if the first name is not provided
                if not first_name:
                    return JsonResponse(
                        NetworkResponse(status='FIRST_NAME_REQUIRED', message=FIRST_NAME_REQUIRED).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

                # if email already exists
                if Validators.is_email_exists(email, CasperUser):
                    return JsonResponse(
                        NetworkResponse(status='STORE_STAFF_ALREADY_EXISTS',
                                        message=STORE_STAFF_ALREADY_EXISTS).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

                # If everything is fine
                staff_data['is_staff'] = True
                staff_data['is_active'] = True

                # generating random password
                temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

                # creating the user
                c_user = CasperUser.objects.create_user(email=email, password=temp_password, first_name=first_name,
                                                        **staff_data)
                # creating the store staff
                staff = StoreStaff(store=store, user=c_user)

                # if the position is provided
                if position:
                    staff.position = position

                # saving the store staff
                staff.save()

                # If the permissions are provided
                if permissions:
                    StaffPermission.objects.create(staff=staff, **permissions)
                else:
                    StaffPermission.objects.create(staff=staff)

                # sending the temp password with email
                text_content = f'Your staff account has been created successfully. Your temporary password is {temp_password}'
                html_content = f'''<div style = "font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2" >
                                    <div style="margin:50px auto;width:70%;padding:20px 0">
                                        <div style="border-bottom:1px solid #eee">
                                        <a href="" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">{store.name}</a>
                                        </div>
                                        <p style="font-size:1.1em">Hey {staff.user.first_name},</p>
                                        <p>Welcome to {store.name}. Your staff account has been created successfully. To access your account use the below temporary password. </p>
                                        <h3 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{temp_password}</h3>
                                        <p style="font-size:0.9em;">Regards,<br />{user.first_name}, Store Admin</p>
                                        <hr style="border:none;border-top:1px solid #eee" />
                                        <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                                        <p>{store.name}</p>
                                        <p>{store.address.city}</p>
                                        </div>
                                    </div>
                                </div>'''
                CasperMail.send_multi_alternative_email(
                    subject=f'Welcome to {store.name}',
                    text_content=text_content,
                    html_content=html_content,
                    to=email)

                # returning the response
                return JsonResponse(
                    NetworkResponse(status='STORE_STAFF_ADDED', message=STORE_STAFF_ADDED).as_dict,
                    status=status.HTTP_201_CREATED)

            # if the store admin has no staff permission
            else:
                return JsonResponse(NetworkResponse(status='NO_STAFF_PERMISSION', message=NO_STAFF_PERMISSION).as_dict,
                                    status=status.HTTP_403_FORBIDDEN)

        # if the user is not a store admin
        else:
            return JsonResponse(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                                status=status.HTTP_401_UNAUTHORIZED)

    # If casper user doesn't exist
    except CasperUser.DoesNotExist:
        return JsonResponse(NetworkResponse(status='USER_NOT_FOUND', message=USER_NOT_FOUND).as_dict,
                            status=status.HTTP_404_NOT_FOUND)

    # If other exceptions occur
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# View to handle store login
@csrf_exempt
def store_login(request):
    if request.method == 'POST':
        try:
            # decode the json data
            data = json.loads(request.body)
            print(data)

            # getting the email and password data from the request
            email = data.get('email')
            password = data.get('password')

            # if the email is none or empty
            if not email or email == '':
                return JsonResponse(NetworkResponse(status='EMAIL_REQUIRED', message=EMAIL_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if the email is not valid
            if Validators.validate_email(email) is False:
                return JsonResponse(NetworkResponse(status='EMAIL_INVALID', message=EMAIL_INVALID).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # if the password is none or empty
            if not password or password == '':
                return JsonResponse(NetworkResponse(status='PASSWORD_REQUIRED', message=PASSWORD_REQUIRED).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)

            # Checking if the password is matching with the email
            user = CasperUser.objects.get(email=email)
            if user.check_password(password):

                # checking if the user is staff or not
                if user.is_staff is False:
                    return JsonResponse(NetworkResponse(status='NOT_A_STORE_STAFF', message=NOT_A_STORE_STAFF).as_dict,
                                        status=status.HTTP_400_BAD_REQUEST)

                # checking if the user is active or not
                if user.is_active is False:
                    return JsonResponse(
                        NetworkResponse(status='ACCOUNT_NOT_ACTIVE', message=ACCOUNT_NOT_ACTIVE).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

                # If everything is fine, then return the token
                jwt_token = JwtToken.get_tokens_for_user(user)
                return JsonResponse(
                    NetworkResponse(status='LOGIN_SUCCESS', message=LOGIN_SUCCESS, data={'token': jwt_token}).as_dict,
                    status=status.HTTP_200_OK)
            else:
                return JsonResponse(NetworkResponse(status='PASSWORD_WRONG', message=PASSWORD_WRONG).as_dict,
                                    status=status.HTTP_400_BAD_REQUEST)
        except CasperUser.DoesNotExist:
            return JsonResponse(NetworkResponse(status='USER_NOT_FOUND', message=USER_NOT_FOUND).as_dict,
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse(
                NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse(NetworkResponse(status='GET_METHOD_NOT_ALLOWED', message=GET_METHOD_NOT_ALLOWED).as_dict,
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
