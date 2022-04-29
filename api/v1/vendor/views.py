from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import NetworkResponse, Address
from store.models import StoreStaff
from common.literals import *
from vendor.serializers import *


# Create your views here.
def vendors(request):
    vendors = Vendor.objects.all()
    serializer = VendorSerializer(vendors, many=True)
    return JsonResponse(serializer.data, safe=False)


# ----------------------------------------@mit----------------------------------------
# Method to add a new vendor
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_vendor(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:
            staff = StoreStaff.objects.get(user=c_user)
            vendor_data = request.data
            address_data = vendor_data.pop('address') if 'address' in vendor_data else None

            if address_data is None:
                return JsonResponse(
                    NetworkResponse(status='VENDOR_ADDRESS_NOT_FOUND', message=VENDOR_ADDRESS_NOT_FOUND).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            if 'name' not in vendor_data:
                return JsonResponse(
                    NetworkResponse(status='VENDOR_NAME_REQUIRED', message=VENDOR_NAME_REQUIRED).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            if 'phone' not in vendor_data:
                return JsonResponse(
                    NetworkResponse(status='VENDOR_PHONE_REQUIRED', message=VENDOR_PHONE_REQUIRED).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            if 'address_line_1' not in address_data or 'city' not in address_data or 'state' not in address_data or 'country' not in address_data or 'pincode' not in address_data:
                return JsonResponse(
                    NetworkResponse(status='VENDOR_ADDRESS_NOT_VALID', message=VENDOR_ADDRESS_NOT_VALID).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # Check if vendor already exists
            temp = Vendor.objects.filter(name=vendor_data['phone'])

            if temp.exists():
                vendor = temp.first()
                store_vendors = StoreVendor(store=staff.store, vendor=vendor, added_by=staff)
                store_vendors.save()
            else:
                # If vendor does not exist, create a new vendor
                address = Address(**address_data)
                address.save()

                vendor = Vendor(address=address, added_by=staff, **vendor_data)
                vendor.save()

                store_vendors = StoreVendor(store=staff.store, vendor=vendor, added_by=staff)
                store_vendors.save()

            return JsonResponse(
                NetworkResponse(status='VENDOR_ADDED', message=VENDOR_ADDED, data=vendor.as_dict).as_dict,
                status=status.HTTP_201_CREATED)

        return JsonResponse(
            NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
            status=status.HTTP_401_UNAUTHORIZED)
    except StoreStaff.DoesNotExist:
        return JsonResponse(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
