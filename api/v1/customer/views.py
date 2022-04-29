from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from common.literals import *
from common.models import NetworkResponse
from common.utils import Validators
from customer.models import Customer
from store.models import StoreStaff


# -----------------------------------@mit-----------------------------------
# Method to add new customer
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_customer(request):
    try:
        # Extracting user from request
        c_user = request.user

        # Checking if user is a store staff and is active
        if c_user.is_staff and c_user.is_active:
            # Getting staff instance from user
            staff = StoreStaff.objects.get(user=c_user)
            # Getting store from staff
            store = staff.store

            # Extracting data from request
            customer_data = request.data

            if 'name' in customer_data or 'email' in customer_data or 'phone' in customer_data:

                if 'email' in customer_data:
                    # if the email is not valid
                    if Validators.validate_email(customer_data.get('email')) is False:
                        return JsonResponse(NetworkResponse(status='EMAIL_INVALID', message=EMAIL_INVALID).as_dict,
                                            status=status.HTTP_400_BAD_REQUEST)

                if 'phone' in customer_data:
                    # if the phone is not valid
                    if Validators.validate_phone_number(customer_data.get('phone')) is False:
                        return JsonResponse(NetworkResponse(status='PHONE_INVALID', message=PHONE_INVALID).as_dict,
                                            status=status.HTTP_400_BAD_REQUEST)

                # Creating new customer
                customer = Customer(**customer_data)
                customer.store = store
                customer.added_by = staff
                customer.save()

                # Creating network response
                network_response = NetworkResponse(
                    status="CUSTOMER_ADDED",
                    message=CUSTOMER_ADDED,
                    data=customer.as_dict
                )

                return JsonResponse(network_response.as_dict, status=status.HTTP_201_CREATED)
            else:
                # Creating network response
                network_response = NetworkResponse(
                    status="CUSTOMER_NAME_OR_PHONE_OR_EMAIL_MISSING",
                    message=CUSTOMER_NAME_OR_PHONE_OR_EMAIL_MISSING
                )

                return JsonResponse(network_response.as_dict, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(
            NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
            status=status.HTTP_401_UNAUTHORIZED)
    except StoreStaff.DoesNotExist:
        return JsonResponse(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------@mit-----------------------------------
# Method to get all customers
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_customers(request):
    try:
        # Extracting user from request
        c_user = request.user

        # Checking if user is a store staff and is active
        if c_user.is_staff and c_user.is_active:
            # Getting staff instance from user
            staff = StoreStaff.objects.get(user=c_user)
            # Getting store from staff
            store = staff.store

            # Getting all customers of store
            customers = Customer.objects.filter(store=store)

            # Creating network response
            network_response = NetworkResponse(
                status="CUSTOMERS_LIST_RETRIEVED",
                message=CUSTOMERS_LIST_RETRIEVED,
                data=[customer.as_dict for customer in customers]
            )

            return JsonResponse(network_response.as_dict, status=status.HTTP_200_OK)

        return JsonResponse(
            NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
            status=status.HTTP_401_UNAUTHORIZED)
    except StoreStaff.DoesNotExist:
        return JsonResponse(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
