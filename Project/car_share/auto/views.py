from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import *
from .managers import *
#from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.contrib.auth.decorators import * 
from .forms import RegistrationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import *
from django.utils.encoding import *

from django.utils.http import *
#from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
#from .forms import EmailConfirmForm
from .tokens import account_activation_token

from django.core.mail import send_mail

EMAIL_HOST_USER = 'whipvic@gmail.com'

@login_required
def index(request):
    customer_list = Customer.objects.order_by('last_name')
    booking_list = Booking.objects.bookings();
    # output = ', '.join([str(customer) for customer in customer_list])
    return render(
        request,
        'index.html',
        context={'customer_list': customer_list, 'booking_list': booking_list},
    )

@login_required
def detail(request, customer_id):
    return HttpResponse("You're viewing customer %s" % customer_id)

'''def logged_in():
    return (Customer.objects.get(id=customer_id)) =='''

@login_required
#@user_passes_test(logged_in)
def bookings(request, customer_id):
    booking_list = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'bookings.html',
        context={'booking_list': booking_list},
    )

@login_required
def profile(request, customer_id):
    current_customer = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'profile.html',
        context={'current_customer': current_customer},
    )

@login_required
def create_booking(request, customer_id):
    current_customer = Customer.objects.get(id=customer_id)
    depot_list = Depot.objects.depots()
    return render(
        request,
        'create_booking.html',
        context={'current_customer': current_customer, 'depot_list': depot_list},
    )

@login_required
def my_bookings(request, customer_id):
    booking_list = Booking.objects.bookings(Customer.objects.get(id=customer_id))
    return render(
        request,
        'my_bookings.html',
        context={'booking_list': booking_list,},
    )


@csrf_exempt
def signup(request):
    """if request.method == "GET":
        form = RegistrationForm()
        return render(request, 'registration_form.html',{'form': form})
    if request.method == "POST":
        form = RegistrationForm(data = request.POST)
        if form.is_valid():
            
            user = form.save()
            user.refresh_from_db()
            user.set_password(user.password)
            user.save()
            user = authenticate(username=user.username, password=request.POST['password1'])
            login(request, user)

            return redirect('index')"""

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            #user = form.instance
            #user.is_active = False
            user = Customer.objects.create_customer(form.cleaned_data['username'], form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['email'], form.cleaned_data['password1'])
            #user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your car_share Account'
            raw_password = form.cleaned_data.get('password1')
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            from_email = EMAIL_HOST_USER
            to_list = [user.email,EMAIL_HOST_USER]
            send_mail(subject, message,from_email,to_list,fail_silently=False, )
            
            return render(request, 'account_activation_sent.html')
            #return redirect('index')
    else:
            form = RegistrationForm()
    return (render(request, 'registration_form.html', {'form': form}))






def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')




@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        #user.email_confirmed = True
        #user.save()
        #login(request, user)
        #return HttpResponse('Thank you for your email confirmation. This is your account.')
        #return redirect(request,'account_activated')
        return render(request, 'account_activated.html')

    else:
        return  HttpResponse('Activation link is invalid!')

'''def account_activated(request):
    return render(request, 'account_activated')'''

