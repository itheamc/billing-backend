from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import NetworkResponse
from store.models import StoreStaff
from vendor.models import StoreVendor
from common.literals import *
from catalogue.models import Product, ProductCategory, ProductMedia, Variant, ProductTax, Attribute
from catalogue.serializers import ProductSerializer


# ----------------------------------@mit----------------------------------
# FUnction to retrieve all products of a store
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser])
def product_list(request):
    try:
        # Getting the instance of the user from the request
        # the user that we are getting here is as per the valid JWT token
        c_user = request.user

        # If user is casper_admin
        if c_user.is_casper_admin and c_user.is_active:
            # Retrieving all products
            products = Product.objects.all()

            # Creating serializer
            serializer = ProductSerializer(products, many=True)

            # Returning the response
            return Response(NetworkResponse(status='PRODUCT_LIST_RETRIEVED', message=PRODUCT_LIST_RETRIEVED,
                                            data=serializer.data).as_dict,
                            status=status.HTTP_200_OK)

        # if user is staff and active
        elif c_user.is_staff and c_user.is_active:
            # Getting the staff instance from the user
            staff = StoreStaff.objects.get(user=c_user)

            # Filtering the products based on the store
            products = Product.objects.filter(store=staff.store)

            # Serializing the products
            serializer = ProductSerializer(products, many=True)

            # Returning the response
            return Response(NetworkResponse(status='PRODUCT_LIST_RETRIEVED', message=PRODUCT_LIST_RETRIEVED,
                                            data=serializer.data).as_dict,
                            status=status.HTTP_200_OK)
        else:
            # if user is inactive or not staff
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If store staff doesn't exist
    except StoreStaff.DoesNotExist:
        return Response(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # if other exception occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to add product media
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
@parser_classes([MultiPartParser])
def add_product_media(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:
            media_data = request.data
            product = None
            variant = None
            if 'product_id' in media_data and media_data['product_id'][0].isnumeric():
                product_id = media_data.pop('product_id')
                product = Product.objects.get(id=int(product_id[0]))
            if 'variant_id' in media_data and media_data['variant_id'][0].isnumeric():
                variant_id = media_data.pop('variant_id')
                variant = Variant.objects.get(id=int(variant_id[0]))

            # if product or variant is none
            if product is None and variant is None:
                return Response(NetworkResponse(status='PRODUCT_OR_VARIANT_ID_MISSING',
                                                message=PRODUCT_OR_VARIANT_ID_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # If image is not present
            if 'image' not in media_data or len(media_data['image']) == 0:
                return Response(NetworkResponse(status='MEDIA_NOT_FOUND', message=MEDIA_NOT_FOUND).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # If image is present
            image = media_data.pop('image')[0]

            # Finally, save the media
            product_media = ProductMedia(product=product, variant=variant, image=image)
            product_media.save()

            # Return the response
            return Response(NetworkResponse(status='PRODUCT_IMAGE_UPLOADED', message=PRODUCT_IMAGE_UPLOADED,
                                            data=product_media.as_dict).as_dict, status=status.HTTP_201_CREATED)
        return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                        status=status.HTTP_401_UNAUTHORIZED)
    except Product.DoesNotExist:
        return Response(NetworkResponse(status='PRODUCT_NOT_FOUND', message=PRODUCT_NOT_FOUND).as_dict,
                        status=status.HTTP_404_NOT_FOUND)
    except Variant.DoesNotExist:
        return Response(NetworkResponse(status='VARIANT_NOT_FOUND', message=VARIANT_NOT_FOUND).as_dict,
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG,
                                        data={'error': str(e)}).as_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to add a new product
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_products(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:
            product_data = request.data
            variant_data = product_data.pop('variants') if 'variants' in product_data else None
            if not variant_data:
                return Response(NetworkResponse(status='VARIANTS_DATA_MISSING', message=VARIANTS_DATA_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            if 'name' not in product_data:
                return Response(NetworkResponse(status='PRODUCT_NAME_MISSING', message=PRODUCT_NAME_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            if 'category' not in product_data:
                return Response(
                    NetworkResponse(status='PRODUCT_CATEGORY_MISSING', message=PRODUCT_CATEGORY_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            if 'vendor' not in product_data:
                return Response(
                    NetworkResponse(status='PRODUCT_VENDOR_MISSING', message=PRODUCT_VENDOR_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            if 'sku' not in product_data:
                return Response(NetworkResponse(status='PRODUCT_SKU_MISSING', message=PRODUCT_SKU_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'cost_price' in variant]) != len(variant_data):
                return Response(
                    NetworkResponse(status='VARIANT_COST_PRICE_MISSING', message=VARIANT_COST_PRICE_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'selling_price' in variant]) != len(variant_data):
                return Response(
                    NetworkResponse(status='VARIANT_SELLING_PRICE_MISSING',
                                    message=VARIANT_SELLING_PRICE_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'mrp' in variant]) != len(variant_data):
                return Response(NetworkResponse(status='VARIANT_MRP_MISSING', message=VARIANT_MRP_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            if len([variant for variant in variant_data if 'sku' in variant]) != len(variant_data):
                return Response(NetworkResponse(status='VARIANT_SKU_MISSING', message=VARIANT_SKU_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'quantity' in variant]) != len(variant_data):
                return Response(
                    NetworkResponse(status='VARIANT_QUANTITY_MISSING', message=VARIANT_QUANTITY_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'tax' in variant]) != len(variant_data):
                return Response(NetworkResponse(status='VARIANT_TAX_MISSING', message=VARIANT_TAX_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            if len([variant for variant in variant_data if 'attributes' in variant]) != len(variant_data):
                return Response(
                    NetworkResponse(status='VARIANT_ATTRIBUTES_MISSING', message=VARIANT_ATTRIBUTES_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if everything is fine
            # retrieving the instances of the models linked with the product
            staff_user = StoreStaff.objects.get(user=c_user)
            store = staff_user.store
            category = ProductCategory.objects.get(id=product_data['category'])
            vendor = StoreVendor.objects.get(id=product_data['vendor'])
            # remove the category and vendor from the product data
            product_data.pop('category')
            product_data.pop('vendor')
            # adding the product
            product = Product(store=store, added_by=staff_user, category=category, vendor=vendor,
                              **product_data)
            product.save()

            # then add the variants
            for variant in variant_data:
                # removing the tax and attributes from the variant data
                tax_data = variant.pop('tax')
                attributes_data = variant.pop('attributes')
                # adding the variant
                variant_obj = Variant(product=product, added_by=staff_user, **variant)
                variant_obj.save()
                # adding the tax for variant
                tax = ProductTax(variant=variant_obj, **tax_data)
                tax.save()
                # then add the attributes
                for attribute in attributes_data:
                    attribute_obj = Attribute(variant=variant_obj, **attribute)
                    attribute_obj.save()

            return Response(NetworkResponse(status='PRODUCT_ADDED', message=PRODUCT_ADDED).as_dict,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)
    except StoreStaff.DoesNotExist:
        return Response(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)
    except StoreVendor.DoesNotExist:
        return Response(NetworkResponse(status='VENDOR_NOT_FOUND', message=VENDOR_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)
    except ProductCategory.DoesNotExist:
        return Response(NetworkResponse(status='CATEGORY_NOT_FOUND', message=CATEGORY_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)
    except ProductMedia.DoesNotExist:
        return Response(NetworkResponse(status='MEDIA_NOT_FOUND', message=MEDIA_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to add product
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_product(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting product data from the request
            product_data = request.data

            # If product name is not in the request or is empty
            if 'name' not in product_data or product_data['name'] == '':
                return Response(NetworkResponse(status='PRODUCT_NAME_MISSING', message=PRODUCT_NAME_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # If category is not in the request or is empty
            if 'category' not in product_data or product_data['category'] == '':
                return Response(
                    NetworkResponse(status='PRODUCT_CATEGORY_MISSING', message=PRODUCT_CATEGORY_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # If vendor is not in the request or is empty
            if 'vendor' not in product_data or product_data['vendor'] == '':
                return Response(
                    NetworkResponse(status='PRODUCT_VENDOR_MISSING', message=PRODUCT_VENDOR_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # If product sku is not in the request or is empty
            if 'sku' not in product_data or product_data['sku'] == '':
                return Response(NetworkResponse(status='PRODUCT_SKU_MISSING', message=PRODUCT_SKU_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # if everything is fine
            # retrieving the instances of the models linked with the product
            staff = StoreStaff.objects.get(user=c_user)
            category = ProductCategory.objects.get(id=product_data['category'])
            vendor = StoreVendor.objects.get(id=product_data['vendor'])
            # remove the category and vendor from the product data
            product_data.pop('category')
            product_data.pop('vendor')
            # adding the product
            product = Product(store=staff.store, added_by=staff, category=category, vendor=vendor,
                              **product_data)
            # finally, saving the product
            product.save()

            # finally, returning the success response
            return Response(NetworkResponse(status='PRODUCT_ADDED', message=PRODUCT_ADDED).as_dict,
                            status=status.HTTP_201_CREATED)

        # If user is inactive or not a staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If Store Staff with given user doesn't exit
    except StoreStaff.DoesNotExist:
        return Response(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If Product Category with given id doesn't exit
    except ProductCategory.DoesNotExist:
        return Response(NetworkResponse(status='CATEGORY_NOT_FOUND', message=CATEGORY_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If Store Vendor with given id doesn't exit
    except StoreVendor.DoesNotExist:
        return Response(NetworkResponse(status='VENDOR_NOT_FOUND', message=VENDOR_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to add product variant
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_variant(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting variant data from the request
            variant_data = request.data

            # if the product id is not in the variant_data or is empty
            if 'product' not in variant_data or variant_data['product'] == '':
                return Response(
                    NetworkResponse(status='PRODUCT_ID_MISSING', message=PRODUCT_ID_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if the cost_price is not in the variant_data or is empty
            if 'cost_price' not in variant_data or variant_data['cost_price'] == '':
                return Response(
                    NetworkResponse(status='VARIANT_COST_PRICE_MISSING', message=VARIANT_COST_PRICE_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if the selling_price is not in the variant_data or is empty
            if 'selling_price' not in variant_data or variant_data['selling_price'] == '':
                return Response(
                    NetworkResponse(status='VARIANT_SELLING_PRICE_MISSING',
                                    message=VARIANT_SELLING_PRICE_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if the mrp is not in the variant_data or is empty
            if 'mrp' not in variant_data or variant_data['mrp'] == '':
                return Response(NetworkResponse(status='VARIANT_MRP_MISSING', message=VARIANT_MRP_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # if the sku is not in the variant_data or is empty
            if 'sku' not in variant_data or variant_data['sku'] == '':
                return Response(NetworkResponse(status='VARIANT_SKU_MISSING', message=VARIANT_SKU_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # if the quantity is not in the variant_data or is empty
            if 'quantity' not in variant_data or variant_data['quantity'] == '':
                return Response(
                    NetworkResponse(status='VARIANT_QUANTITY_MISSING', message=VARIANT_QUANTITY_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if the tax is not in the variant_data or is None
            if 'tax' not in variant_data or variant_data['tax'] is None:
                return Response(NetworkResponse(status='VARIANT_TAX_MISSING', message=VARIANT_TAX_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # if the attributes is not in the variant_data or is None
            if 'attributes' not in variant_data or variant_data['attributes'] is None:
                return Response(
                    NetworkResponse(status='VARIANT_ATTRIBUTES_MISSING', message=VARIANT_ATTRIBUTES_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if everything is fine
            # retrieving the instances of the models linked with the product
            staff = StoreStaff.objects.get(user=c_user)

            product_id = variant_data.pop('product')
            product = Product.objects.get(id=product_id)

            # removing the tax and attributes from the variant data
            tax_data = variant_data.pop('tax')
            attributes_data = variant_data.pop('attributes')

            # adding the variant
            variant_obj = Variant(product=product, added_by=staff, **variant_data)
            variant_obj.save()

            # adding the tax for variant
            tax = ProductTax(variant=variant_obj, **tax_data)
            tax.save()

            # then add the attributes
            for attribute in attributes_data:
                attribute_obj = Attribute(variant=variant_obj, **attribute)
                attribute_obj.save()

            # Finally, returning the success response
            return Response(NetworkResponse(status='VARIANT_ADDED', message=VARIANT_ADDED).as_dict,
                            status=status.HTTP_201_CREATED)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If Staff with given user doesn't exit
    except StoreStaff.DoesNotExist:
        return Response(NetworkResponse(status='STAFF_NOT_FOUND', message=STAFF_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)
    # If Product with given id doesn't exit
    except Product.DoesNotExist:
        return Response(NetworkResponse(status='PRODUCT_NOT_FOUND', message=PRODUCT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to add attribute
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_attribute(request):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting variant attribute data from the request to update
            attribute_data = request.data

            # if variant id is not in the attribute_data or is None
            if 'variant' not in attribute_data or attribute_data['variant'] is None or attribute_data['variant'] == '':
                return Response(NetworkResponse(status='VARIANT_ID_MISSING', message=VARIANT_ID_MISSING).as_dict,
                                status=status.HTTP_400_BAD_REQUEST)

            # if name is not in the attribute_data or is None
            if 'name' not in attribute_data or attribute_data['name'] is None or attribute_data['name'] == '':
                return Response(
                    NetworkResponse(status='ATTRIBUTE_NAME_MISSING', message=ATTRIBUTE_NAME_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # if value is not in the attribute_data or is None
            if 'value' not in attribute_data or attribute_data['value'] is None or attribute_data['value'] == '':
                return Response(
                    NetworkResponse(status='ATTRIBUTE_VALUE_MISSING', message=ATTRIBUTE_VALUE_MISSING).as_dict,
                    status=status.HTTP_400_BAD_REQUEST)

            # Retrieving variant instance
            variant_id = attribute_data.pop('variant')
            variant = Variant.objects.get(id=variant_id)

            # Adding the attribute
            attribute = Attribute(variant=variant, **attribute_data)
            attribute.save()

            # Returning the success response
            return Response(NetworkResponse(status='ATTRIBUTE_ADDED', message=ATTRIBUTE_ADDED).as_dict,
                            status=status.HTTP_201_CREATED)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If Variant with given id doesn't exit
    except Variant.DoesNotExist:
        return Response(NetworkResponse(status='VARIANT_NOT_FOUND', message=VARIANT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to update product
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_product(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting product data from the request to update
            product_data = request.data

            # Retrieving product instance
            product = Product.objects.get(id=pk)

            # if product name attribute is in the product_data and not empty
            if 'name' in product_data and product_data['name'] is not None and not product_data['name'] == '':
                product.name = product_data['name']

            # if product description attribute is in the product_data and not empty
            if 'description' in product_data and product_data['description'] is not None and not product_data[
                                                                                                     'description'] == '':
                product.description = product_data['description']

            # if product category id is in the product_data and not empty
            if 'category' in product_data and product_data['category'] is not None and not product_data[
                                                                                               'category'] == '':
                category = ProductCategory.objects.get(id=product_data['category'])
                product.category = category

            # if product tags attribute is in the product_data and not empty
            if 'tags' in product_data and product_data['tags'] is not None and not len(product_data['tags']) > 0:
                product.tags = product_data['tags']

            # if product is_active attribute is in the product_data and not empty
            if 'is_active' in product_data and product_data['is_active'] is not None:
                product.is_active = product_data['is_active']

            # Finally, saving the updated product
            product.save()

            # Returning the success response
            return Response(NetworkResponse(status='PRODUCT_UPDATED', message=PRODUCT_UPDATED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If Product with given id doesn't exit
    except Product.DoesNotExist:
        return Response(NetworkResponse(status='PRODUCT_NOT_FOUND', message=PRODUCT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If Product Category with given id doesn't exit
    except ProductCategory.DoesNotExist:
        return Response(NetworkResponse(status='CATEGORY_NOT_FOUND', message=CATEGORY_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to update product variant
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_variant(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting product variant data from the request to update
            variant_data = request.data

            # Retrieving product variant instance
            variant = Variant.objects.get(id=pk)

            # if cost_price attribute is in the variant_data and not empty
            if 'cost_price' in variant_data and variant_data['cost_price'] is not None and not variant_data[
                                                                                                   'cost_price'] == '':
                variant.cost_price = variant_data['cost_price']

            # if selling_price attribute is in the variant_data and not empty
            if 'selling_price' in variant_data and variant_data['selling_price'] is not None and not variant_data[
                                                                                                         'selling_price'] == '':
                variant.selling_price = variant_data['selling_price']

            # if mrp id is in the variant_data and not empty
            if 'mrp' in variant_data and variant_data['mrp'] is not None and not variant_data['mrp'] == '':
                variant.mrp = variant_data['mrp']

            # if quantity attribute is in the variant_data and not empty
            if 'quantity' in variant_data and variant_data['quantity'] is not None and not variant_data[
                                                                                               'quantity'] == '':
                variant.quantity = variant_data['quantity']

            # if product is_active attribute is in the variant_data and not empty
            if 'is_active' in variant_data and variant_data['is_active'] is not None:
                variant.is_active = variant_data['is_active']

            # Finally, saving the updated product variant
            variant.save()

            # Returning the success response
            return Response(NetworkResponse(status='VARIANT_UPDATED', message=VARIANT_UPDATED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If variant with given id doesn't exit
    except Variant.DoesNotExist:
        return Response(NetworkResponse(status='VARIANT_NOT_FOUND', message=VARIANT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to update product variant attribute
@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def update_attribute(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Extracting attribute data from the request to update
            attribute_data = request.data

            # Retrieving attribute instance
            attribute = Attribute.objects.get(id=pk)

            # if name is in the attribute_data and not empty
            if 'name' in attribute_data and attribute_data['name'] is not None and not attribute_data['name'] == '':
                attribute.name = attribute_data['name']

            # if value is in the attribute_data and not empty
            if 'value' in attribute_data and attribute_data['value'] is not None and not attribute_data['value'] == '':
                attribute.value = attribute_data['value']

            # if unit is in the attribute_data and not empty
            if 'unit' in attribute_data and attribute_data['unit'] is not None and not attribute_data['unit'] == '':
                attribute.unit = attribute_data['unit']

            # Finally, saving the updated attribute
            attribute.save()

            # Returning the success response
            return Response(NetworkResponse(status='ATTRIBUTE_UPDATED', message=ATTRIBUTE_UPDATED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If attribute with given id doesn't exit
    except Attribute.DoesNotExist:
        return Response(NetworkResponse(status='ATTRIBUTE_NOT_FOUND', message=ATTRIBUTE_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to delete product
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_product(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Retrieving product instance
            product = Product.objects.get(id=pk)

            # Deleting product
            product.delete()

            # Returning the success response
            return Response(NetworkResponse(status='PRODUCT_DELETED', message=PRODUCT_DELETED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If product with given id doesn't exit
    except Product.DoesNotExist:
        return Response(NetworkResponse(status='PRODUCT_NOT_FOUND', message=PRODUCT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to delete product
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_variant(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Retrieving variant instance
            variant = Variant.objects.get(id=pk)

            # Deleting variant
            variant.delete()

            # Returning the success response
            return Response(NetworkResponse(status='VARIANT_DELETED', message=VARIANT_DELETED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If variant with given id doesn't exit
    except Variant.DoesNotExist:
        return Response(NetworkResponse(status='VARIANT_NOT_FOUND', message=VARIANT_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to delete product attribute
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_attribute(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Retrieving attribute instance
            attribute = Attribute.objects.get(id=pk)

            # Deleting attribute
            attribute.delete()

            # Returning the success response
            return Response(NetworkResponse(status='ATTRIBUTE_DELETED', message=ATTRIBUTE_DELETED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If variant with given id doesn't exit
    except Attribute.DoesNotExist:
        return Response(NetworkResponse(status='ATTRIBUTE_NOT_FOUND', message=ATTRIBUTE_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------@mit----------------------------------
# Function to delete product media
@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def delete_product_media(request, pk):
    try:
        c_user = request.user
        if c_user.is_staff and c_user.is_active:

            # Retrieving media instance
            media = ProductMedia.objects.get(id=pk)

            # Deleting product media
            media.delete()

            # Returning the success response
            return Response(NetworkResponse(status='PRODUCT_IMAGE_DELETED', message=PRODUCT_IMAGE_DELETED).as_dict,
                            status=status.HTTP_200_OK)

        # if user is inactive or not staff
        else:
            return Response(NetworkResponse(status='UNAUTHORIZED', message=UNAUTHORIZED).as_dict,
                            status=status.HTTP_401_UNAUTHORIZED)

    # If product media with given id doesn't exit
    except ProductMedia.DoesNotExist:
        return Response(NetworkResponse(status='PRODUCT_IMAGE_NOT_FOUND', message=PRODUCT_IMAGE_NOT_FOUND).as_dict,
                        status=status.HTTP_400_BAD_REQUEST)

    # If any error other than specified above occurs
    except Exception as e:
        return Response(NetworkResponse(status='WENT_WRONG', message=WENT_WRONG, data={'error': str(e)}).as_dict,
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)