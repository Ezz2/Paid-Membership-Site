from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from django.contrib.auth.models import User

from .models import FitnessPlan, Customer
from .forms import CustomSignupForm

stripe.api_key = "sk_test_51NfoavAOoyyhXMiqRawiy6SoIYXdPKf7j8zclCaPknRF1yquqjZ4YNTibVvZMpj0nscOjwM8rF1OMVZyexTAPj1n006vxAXHH4"

# @user_passes_test(lambda u: u.is_active)
# def updateaccounts(request):
#     customers = Customer.objects.all()
    
#     for customer in customers:
#         subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
#         if subscription.status == 'canceled':
#             customer.membership = False
#         else:
#             customer.membership = True
            
#         customer.cancel_at_period_end = subscription.cancel_at_period_end
#         customer.save()
#         return HttpResponse("Completed")

def home(request):
    plans = FitnessPlan.objects.all()
    return render(request, 'plans/home.html', {"plans": plans})

class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid

def plan(request, pk):
    plan = get_object_or_404(FitnessPlan, pk=pk)
    
    if plan.premium:
        try:
            if request.user.customer.membership == False and request.user.customer.cancel_at_period_end == True:
                return redirect('/') 
        except:
            return redirect('join')
        
        if request.user.is_authenticated:
            try:
                if request.user.customer.membership:
                    return render(request, 'plans/plan.html', {'plan': plan})
            except Customer.DoesNotExist:
                return redirect('join')
        return redirect('join')
    else:
        return render(request, 'plans/plan.html', {'plan': plan})

def join(request):
    return render(request, 'plans/join.html')

@login_required()
def checkout(request):
    plan = FitnessPlan.objects.all()
    
    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass
    
    coupons = {'hallowen': 31, 'welcome': 10}
    if request.method == 'POST':
        
        stripe_customer = stripe.Customer.create(name=request.user, email=request.user.email, source='tok_visa')
        
        plan = 'price_1NfohFAOoyyhXMiqNu4BUnVo'
        if request.POST['plan'] == 'yearly':
            plan = 'price_1NfokuAOoyyhXMiqmnwX0DIh'
        if request.POST['coupon'] in coupons:
            percentage = coupons[request.POST['coupon'].lower()]
            print(percentage)
            try:
                coupon = stripe.Coupon.create(duration='once', percent_off=percentage, name=request.POST['coupon'])
            except:
                pass
            
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
            items=[{'plan':plan}])
            coupon=request.POST['coupon'].lower(),
        else:
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
            items=[{'plan':plan}])

        customer = Customer()
        customer.user = request.user
        customer.stripe = stripe_customer.id
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = subscription.id
        customer.save()

        return redirect('home')
    else:
        plan = 'monthly'
        coupon = 'none'
        og_dollar = 10
        coupon_dollar = 0
        final_dollar = 10
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'yearly':
                plan = 'yearly'
                og_dollar = 100
                final_dollar = 100
                
        if request.method == 'GET' and 'coupon' in request.GET:
            if request.GET['coupon'].lower() in coupons:
                
                coupon = request.GET['coupon'].lower()
                percentage = coupons[coupon]
                coupon_price = int((percentage / 100) * og_dollar)
                final_dollarr = int(og_dollar - coupon_price)
                coupon_dollar = percentage
                final_dollar = final_dollarr
                
        return render(request, 'plans/checkout.html', {'plan': plan, 'coupon':coupon, 'og_dollar':og_dollar,
                                'coupon_dollar':coupon_dollar, 'final_dollar':final_dollar})

@user_passes_test(lambda u: u.is_active)
def settings(request):
    
    try:
        if request.user.customer.membership == True:
            membership = True
            cancel_at_period_end = False
        else:
            membership = False
            cancel_at_period_end = False
    except Customer.DoesNotExist:
        return redirect('join')
        
    if request.method == "POST":
        
        subscription = stripe.Customer.delete(request.user.customer.stripe)
        subscription.save()
        
        delete_database = User.objects.get(id=request.user.id)
        delete_database.delete()
        return redirect('/')
        
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
                
        except Customer.DoesNotExist:
            membership = False
        
    return render(request, 'registration/settings.html', {'membership':membership,
                'cancel_at_period_end':cancel_at_period_end})

@login_required()
def myprofile(request):
    profile = Customer.objects.all()
    return render(request, 'registration/myprofile.html', {'profile':profile})
