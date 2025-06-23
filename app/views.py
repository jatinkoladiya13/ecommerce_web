from django.shortcuts import render, redirect, get_object_or_404
import stripe.http_client
from app.models import User, Category, Product, ProductImage,Brand,CartItem, OrderItems
from django.contrib import messages
from app.commonpassword import commonpasswordCheck
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from app.emailhelper import Util
from xml.dom import ValidationErr
from .decorators import login_required, superuser_required, admin_login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt 
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator
from .untils import encrypt, decrypt
import os
import json
import razorpay
import stripe


# Create your views here.

def homepage(request):
    
    products = Product.objects.prefetch_related('images').all()

    return render(request, 'index.html',{'products': products})


def shoppage(request):
    query = request.GET.get('q', '')
    page_number = request.GET.get('page')
    if query:
        product_object = Product.objects.prefetch_related('images').filter(productName__icontains=query)
        paginator = Paginator(product_object, 6)
        showData = paginator.get_page(page_number)
        return render(request, 'shop.html', {"data": showData})


    
    product_data = Product.objects.prefetch_related('images').all()
    paginator = Paginator(product_data, 6)

    showData = paginator.get_page(page_number)
    return render(request, 'shop.html', {"data": showData})

# /search/?q=
def search_items(request):
    query = request.GET.get('q')
    playload = []
    if query:
        product_object = Product.objects.filter(productName__icontains=query)
        for product in product_object:
            playload.append(product.productName) 

        return JsonResponse({"data":playload}, )
    
    return JsonResponse({'error': 'Invalid request'}, status=400)    


def blogpage(request):
    return render(request, 'blog.html')

def aboutpage(request):
    return render(request, 'about.html')

def contactpage(request):
    return render(request, 'contact.html')


def wishlistpage(request):
    return render(request, 'Wishlist.html')



@login_required
def cartpage(request,  product_id=None):
    if product_id:
        products_data = Product.objects.prefetch_related('images').get(id=product_id)
        image_url = products_data.images.first().image_file.url 
            
        if CartItem.objects.filter(product=products_data).exists():
            return redirect('cart')
        else :
            add_cart = CartItem.objects.create(user = request.user, product=products_data, quantity=1, image_url=image_url)
            if  add_cart:
                add_cart.save()
                messages.success(request, "Your product add in cart successfully!")
                return redirect('cart')
   
   
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'cart.html', {'cart_items':cart_items, 'key': settings.STRIPE_PUBLISHABLE_KEY})

@csrf_exempt
def remove_from_cart(request):
    
    if request.method == 'POST' :
        json_id = json.loads(request.body)
        cart_items_id = json_id.get("cart_item_id")
        try:
           create_item =   CartItem.objects.get(id=cart_items_id, user = request.user)
           create_item.delete()  
           return JsonResponse({'message': 'Item removed successfully'}, status=200) 

        except CartItem.DoesNotExist:
        
            pass
    return JsonResponse({'error': 'Invalid request'}, status=400)    


@csrf_exempt
def update_quantity_cart(request):
    if request.method == 'POST':
        json_id=json.loads(request.body)
        cart_items_id = json_id.get("cart_item_id")
        update_quantity = json_id.get("update_quantity")
        try:
            create_item =   CartItem.objects.get(id=cart_items_id, user = request.user)
            create_item.quantity = update_quantity;  
            create_item.save()
            return JsonResponse({'message': 'Item removed successfully'}, status=200) 
        except CartItem.DoesNotExist:
            pass

    return JsonResponse({'error': 'Invalid request'}, status=400)  

@csrf_exempt
@login_required
def pay_order(request):

    if request.method == 'POST':
        json_id = json.loads(request.body)
        amount = int(json_id.get("amount").replace(',', '')) * 100
        if amount:
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
            payment = client.order.create({'amount':amount,'currency':'INR', 'payment_capture':1})
            return JsonResponse(payment, status=200) 
    return JsonResponse({'error': 'Invalid request'}, status=400)    
        
@login_required
def success_payment(request):
    cart_Data = CartItem.objects.filter(user = request.user)
    if cart_Data:
        for data in cart_Data:
            orderItems = OrderItems.objects.create(user = request.user, product = data.product, image_url = data.image_url, quantity = data.quantity)
            orderItems.save()
        CartItem.objects.filter(user = request.user).delete()
        return redirect('home')

def orders(request):
    order_data = OrderItems.objects.filter(user = request.user)
    return render(request, 'orders.html',{'order_items':order_data} )

def  sproductpage(request, product_id):
    products_data = Product.objects.prefetch_related('images').get(id=product_id)
    images = products_data.images.all()       
     
    fillter_data = Product.objects.prefetch_related('images').filter(category = products_data.category)
     
    return render(request, 'sproduct.html', {'productsData': products_data,  'images':images, 'data': fillter_data})

def loginpage(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(email, password)
        if User.objects.filter(email=email).exists():
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Your login successfully!")
                return redirect('home') 
            else:
                messages.error(request, "Bad carditional") 
        else:
            messages.success(request, "Email not existed") 

    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        mobile_number = request.POST['mobileNumber']
        password = request.POST['password']

        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return render(request, 'signup.html')
        
        # pat = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # if re.match(pat,email) is not True:
        #     messages.error(request, "Enter valid email")
        #     return render(request, 'signup.html')
        
        result = commonpasswordCheck(password=password)
        if result is not True:
            messages.error(request, result)
            return render(request, 'signup.html')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "This username is already taken. Please choose another one.")
            return render(request, 'signup.html')
        
        if User.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, "This username is already taken. Please choose another one.")
            return render(request, 'signup.html')
        
        stripe_customer = stripe.Customer.create(
            email=email,
            name=username,
        )
         

        myUser = User.objects.create_user(username=username, email=email, mobile_number=mobile_number, password=password, stripe_customer_id=stripe_customer['id'])
        myUser.save()
        messages.success(request, "Your account has been registered successfully!")
        return redirect('home')
        
    return render(request, 'signup.html')

def sendlink(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user=user)
            link = f"http://localhost:8000/resetpassword/{uid}/{token}"
            html_body = f'Clik following link to reset your password <a href="{link}">{link}</a>'
            data = {
                "subject": "REset your password",
                "body":'Click the following link to reset your password:',
                "html_boUtil.send_email(data=data)dy": html_body,
                "to_email": user.email
            }
            
            Util.send_email(data=data)
            messages.success(request, "Your resetpasswrod link send your email successfully!")
            return redirect('login')
        else:
            messages.error(request, "This email is not exists..!")
            return render(request, 'sendlink.html')
        
    return render(request, 'sendlink.html')

def resetpassword(request, uid, token):
    if request.method == 'POST':
        password = request.POST['password']

        result = commonpasswordCheck(password=password)
        if result is not True:
            messages.error(request, result)
            return render(request, 'resetpassword.html')
        
        try:
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user=user, token=token):
                messages.error(request, "Token is not valid or Expired")
                return render(request, "resetpassword.html") 
            user.set_password(password)
            user.save()
            messages.success(request, "Your password reset successfully..!")
            return redirect('login')
        
        except  DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user=user, token=token)
            raise ValidationErr('Token is not valid or Expired')          
    
    return render(request, 'resetpassword.html')


def signout(request):
    logout(request)
    messages.success(request,"Log out successfully..!")
    return redirect('home')

@login_required
def userprofile(request):
    user = request.user
    if request.method  == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        mobile_number = request.POST['mobileNumber']

        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return render(request, "userprofile.html")
        user = User.objects.get(id=request.user.id)
        # if User.objects.filter(email=email).exists():
        #     messages.error(request, "This username is already taken. Please choose another one.")
        #     return render(request, 'userprofile.html')
        
        # if User.objects.filter(mobile_number=mobile_number).exists():
        #     messages.error(request, "This username is already taken. Please choose another one.")
        #     return render(request, 'userprofile.html')
        
        
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.mobile_number = mobile_number
        user.save()
        messages.success(request, "Your profile update successfully..!")
        print(first_name, last_name, username, email, mobile_number)

    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'user_name': user.username,
        'user_email': user.email,
        'mobileNumber': user.mobile_number 
    }

    return render(request, "userprofile.html",{'initial_data': initial_data})

@login_required
@superuser_required
def dashboard(request):
    return render(request, "dashboard.html")


@login_required
@superuser_required
def category(request):
    if request.method == 'POST':
        category = request.POST['category']

        if Category.objects.filter(category_name=category).exists():
            messages.error(request, "This category is already taken. Please choose another one.")
            return render(request, 'category.html')
        
        if category:
            category_create = Category.objects.create(category_name = category, isDeleted = True)
            category_create.save()
            messages.success(request,"category save successfully..!")
            return render(request, 'category.html')
         
    return render(request, "category.html")


def category_view(request):
    category = Category.objects.filter(isDeleted = True)

    return render(request, "categoryview.html", {"data": category})

@csrf_exempt
def category_delete(request):
    if request.method == 'POST':
        json_id = json.loads(request.body)
        category_id = json_id.get("category_id")
        
        try:
            category = Category.objects.get(id=category_id)
            category.isDeleted = False
            category.save()
            return JsonResponse({'message': 'Category removed successfully'}, status=200) 
        except Category.DoesNotExist:
            pass    

    return JsonResponse({'error': 'Invalid request'}, status=400)  

@csrf_exempt
def category_update(request):
    if  request.method == 'POST':
        json_id = json.loads(request.body)
        category_id = json_id.get("category_id")
        categoryName = json_id.get("categoryName")
        
        if categoryName :
            try:
                category = Category.objects.get(id=category_id)
                category.category_name = categoryName
                category.save()
                return JsonResponse({'message': 'Category update successfully'}, status=200) 
            except Category.DoesNotExist:
                pass  
        else:
            return JsonResponse({'error': 'Category Empty'}, status=400)  


    return JsonResponse({'error': 'Invalid request'}, status=400)  


@login_required
@superuser_required
def brand(request):
    if request.method == 'POST':
        brand_name = request.POST['brand']

        if Brand.objects.filter(brand_name=brand_name).exists():
            messages.error(request, "This Brand Name is already taken. Please choose another one.")
            return render(request, 'brand.html')

        if brand_name:
            brand = Brand.objects.create(brand_name=brand_name, isDeleted = True)
            brand.save()
            messages.success(request,"Brand name save successfully..!")
            return render(request, 'brand.html')

    return render(request, "brand.html")


def brand_view(request):
    brand = Brand.objects.filter(isDeleted = True)
    return render(request, "brandview.html",{"brand":brand})

@csrf_exempt
def brand_delete(request):
    
    if request.method == 'POST':
        json_id = json.loads(request.body)
        brand_id = json_id.get("brand_id")

        try:
            brand =  Brand.objects.get(id=brand_id)
            brand.isDeleted = False
            brand.save()
            return JsonResponse({'message': 'Brand removed successfully'}, status=200) 
          
        except Brand.DoesNotExist:
            pass    

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def brand_update(request):
    if request.method == 'POST':
        json_id = json.loads(request.body)
        brand_id = json_id.get("brand_id")
        brand = json_id.get('brand')

        try:
            brandModel =  Brand.objects.get(id=brand_id)
            brandModel.brand_name = brand
            brandModel.save()
            return JsonResponse({'message': 'This Brand  successfully update'}, status=200) 
          
        except Brand.DoesNotExist:
            pass    

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@superuser_required
def product_add(request):
   
    if request.method == 'POST':
        product_name = request.POST['product_name'] 
        description = request.POST['description']
        price = request.POST['price']
        category_id = request.POST['last_name']
        brand_id = request.POST['brand']
        images = request.FILES.getlist('upload')
        
        
        if not (product_name and description and price and images  and category_id):
            messages.error(request, "Please provide all required information.")
            return JsonResponse({'error': 'Please provide all required information.'}, status=400)
            
        
        
        if Product.objects.filter(productName=product_name).exists():
            messages.error(request,"This product already exists..!")
            return JsonResponse({'error': 'This product already exists..!'}, status=400)
        
        
        selected_category = Category.objects.get(id=category_id)
        selected_brand = Brand.objects.get(id=brand_id)
        product = Product.objects.create(user=request.user, productName=product_name, description=description, rate=price, category=selected_category, brand=selected_brand)
        product.save()
    
        for uploaded_file in images:
                    product_image = ProductImage.objects.create(product=product, image_file=uploaded_file) 
                    product_image.save()
            

        messages.success(request,"Publish  successfully..!")
        return JsonResponse({'redirect_url': reverse('dashboard')}, status=200)
    

    category = Category.objects.filter(isDeleted = True)
    brand = Brand.objects.filter(isDeleted = True)
    context = {
        'categorys': category,
        'brands':brand,
        'mode' : 'add',
    }
    return render(request, "productadd.html", context)


def product_view(request):
    products = Product.objects.all() 
    encrypted_products = [
        {
            "id": product.id,
            "user":product.user,
            "productName":product.productName,
            "description": product.description,
            "rate":product.rate,
            "category":product.category,
            "brand":product.brand, 
            'encrypted_id': encrypt(str(product.id))
        }
        for product in products
    ]
    return render(request, "productview.html", {"products":encrypted_products})

@csrf_exempt
def product_delete(request):
    if request.method == 'POST':
        json_id = json.loads(request.body)
        product_id = json_id.get("product_id")

        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'message': 'Product delete successfully......!'}, status=200)
        except Product.DoesNotExist:
            pass    

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@superuser_required
def product_update(request, encrypted_id):
    
    product_id = int(decrypt(encrypted_id))
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product_name = request.POST['product_name'] 
        description = request.POST['description']
        price = request.POST['price']
        category_id = request.POST['last_name']
        brand_id = request.POST['brand']
        images = request.FILES.getlist('upload')
    
        

        print(f"========={product_name}==========", product_name == '')      
        
        if not (product_name and description and price and images  and category_id):
            messages.error(request, "Please provide all required information.")
            return JsonResponse({'error': 'Please provide all required information.'}, status=400)
        
        # if Product.objects.filter(productName=product_name).exists():
        #     messages.error(request,"This product already exists..!")
        #     return redirect('product_update/product_id/')
        
        
        product.productName = product_name
        product.description = description
        product.rate = price
        product.category = Category.objects.get(id=category_id)
        product.brand = Brand.objects.get(id=brand_id)
        product.save()

        for img in product.images.all():
            img.delete()

        for image in images:
            ProductImage.objects.create(product=product, image_file=image)
            
        
        messages.success(request,"This product Update   successfully..!")
        return JsonResponse({'redirect_url': reverse('product_view')}, status=200)



    images = product.images.all()       
    category = Category.objects.filter(isDeleted = True)
    brand = Brand.objects.filter(isDeleted = True)
    

    
    context ={
    'mode' : 'update',
    'images':images,
    'product':product,
    'categorys': category,
    'brands':brand,
    'encrypted_id':encrypt(str(product.id)),
    }
    return render(request, "productupdate.html", context)


def network_error(request):
    return render(request, "networkerror.html")

stripe.api_key = settings.STRIPE_SECRET_KEY
def checkout_session(request,user_id):
    cart_items = CartItem.objects.filter(user = user_id)
    
    total = 0

    for ite in cart_items:
        total  += int(ite.quantity) * int(ite.product.rate * 100) 
        session = stripe.PaymentIntent.create(
		payment_method_types=['card'],
        customer= request.user.stripe_customer_id,
		line_items=[{
	      'price_data': {
	        'currency': 'inr',
	        'product_data': {
	          'name': "Cart All Items",
	        },
	        'unit_amount': total,
	      },
	      'quantity': 1,
	    }],
	     mode='payment',

	    success_url='http://127.0.0.1:8000/pay_success?session_id={CHECKOUT_SESSION_ID}',
	    cancel_url='http://127.0.0.1:8000/login/',
	    client_reference_id=user_id
	)
    return redirect(session.url, code=303)


def pay_success(request):
    session = stripe.checkout.Session.retrieve(request.GET['session_id'])
    user_id=session.client_reference_id
    cart_items = CartItem.objects.filter(user = user_id) 
    if cart_items:
        for data in cart_items:
            ordersItems = OrderItems.objects.create(user = request.user, product = data.product, image_url = data.image_url, quantity = data.quantity)
            ordersItems.save()
        CartItem.objects.filter(user = request.user).delete() 
        return redirect('home')
    return render(request, 'cart.html')



def subscriptions(request):
        if request.user.is_authenticated:
            subscriptions_id = request.user.stripe_subscription_id
            subscriptions = stripe.Subscription.retrieve(subscriptions_id)
            return render(request, "subscriptions.html",{'subscription': subscriptions,})
       


def checkout_subscription(request,amount):

    if amount:  
        
        session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        customer= request.user.stripe_customer_id,
        line_items=[{
            'price_data': {
            'currency': 'inr',
            'product_data': {
                'name': "Cart All Items",
            },
            'recurring': {
                        'interval': 'month',
                        'interval_count': 1,
                    },

            'unit_amount': int(amount * 100),
            },
            'quantity': 1,
        }],
            mode='subscription',

        success_url='http://127.0.0.1:8000/subscription_pay_succcess?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://127.0.0.1:8000/subscriptions/',
        client_reference_id=request.user.id 
    )
        
    return redirect(session.url, code=303)


def subscription_pay_succcess(request):
    session = stripe.checkout.Session.retrieve(request.GET['session_id'])
    user_id=session.client_reference_id
    user = User.objects.get(id = user_id)
    
    if user:
        subscription_id = session.subscription
        user.is_subscrib = True
        user.stripe_subscription_id = subscription_id
        user.save()
        return redirect('subscriptions')
    return render(request, "subscriptions.html")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': str(e)}, status=400)
     
    try :
        if event['type'] in ['invoice.payment_succeeded', 'customer.subscription.created']:
            customer_id =  event['data']['object']['customer']
            user = User.objects.get(stripe_customer_id  = customer_id)
            user.is_subscrib = True
            user.save()
        elif event['type'] == 'customer.subscription.deleted':
            customer_id =  event['data']['object']['customer']
            user = User.objects.get(stripe_customer_id  = customer_id)
            user.is_subscrib = False
            user.save()
        elif event['type'] == 'invoice.payment_failed' :
            customer_id = event['data']['object']['customer']
            user = User.objects.get(stripe_customer_id  = customer_id)
            user.is_subscrib = False
            user.save()        
        elif event['type'] == 'invoice.payment_succeeded':
            customer_id =  event['data']['object']['customer']
            user = User.objects.get(stripe_customer_id  = customer_id)
            user.is_subscrib = True
            user.save()
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  
    return JsonResponse({'status': 'success'}, status=200)


def update_subscription(request, amount): 
    if amount:  
        try:
            subscription_id = request.user.stripe_subscription_id
            subscription = stripe.Subscription.retrieve(subscription_id)
           
            product = stripe.Product.create(
                name="Cart All Items",
                description="Update Subcription Plans"
            )


            price = stripe.Price.create(
                unit_amount=int(amount * 100),  
                currency='inr',
                recurring={'interval': 'month',
                            'interval_count': 1,}, 
                product=product.id,  
            )
            stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id':subscription['items']['data'][0].id,
                'plan': price.id,
            }]
            )

            return redirect('subscriptions')
        except Exception as e:
          return redirect('subscriptions')


def cancel_subscription(request):
    subscription_id = request.user.stripe_subscription_id

    try:
        stripe.Subscription.delete(subscription_id)
        request.user.is_subscrib = False
        request.user.save()
        return redirect('subscriptions')
    except stripe.error.stripeError as e:
        messages.error(request, str(e)) 
        return redirect('subscriptions')
