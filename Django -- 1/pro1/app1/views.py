from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, logout, login
from .forms import *
from django.core.paginator import Paginator
import requests, random, asyncio
from django.core.mail import send_mail
from django.conf import settings
from googletrans import Translator, LANGUAGES
L = {value.capitalize(): key for key, value in LANGUAGES.items()}


def Home(req):
    return render(req, 'Home.html')


def Register(req):
    if req.method == 'POST':
        nm = req.POST['na']
        em = req.POST['ew']
        pw = req.POST['pq']
        pw1 = req.POST['pq1']
        p = req.FILES['photo']
        Cp = req.POST.get('h-captcha-response')

        if pw != pw1:
            Error = 'Both Password Should Be Match !!'
            return render(req, 'Register.html', context={'Err': Error})

        vb = Users.objects.filter(Email=em).count()
        if vb == 1:
            Error = 'Email Already Exists !!'
            return render(req, 'Register.html', context={'Err': Error})

        else:
            url = 'https://api.hcaptcha.com/siteverify'
            data = {
                'response': Cp,
                'secret': 'ES_120dcfb266604210958a6fc9dc784b89' # your secret key
            }
            response = requests.post(url, data)
            result = response.json()

            if result.get('success'):
                ob = Users(Name=nm, Email=em, Password=make_password(pw), Image=p)
                ob.save()
                ob1 = User(username=em, password=make_password(pw))
                ob1.save()
                return redirect(Login)
            else:
                Error = 'Invalid Captcha !!'
                return render(req, 'Register.html', context={'Err': Error})
    else:
        return render(req, 'Register.html')


def Login(req):
    v = CP(req.POST)
    if req.method == 'POST':
        email = req.POST['em']
        password = req.POST['pw']
        try:
            Record = Users.objects.get(Email=email)
            if check_password(password, Record.Password):
                Auth = authenticate(username=email, password=password)
                if Auth is not None:
                    print(Auth)
                    login(req, Auth)
                    if v.is_valid():
                        if Record.Role == 'Admin':
                            return redirect(DashBoard)
                        else:
                            req.session['U_id'] = Record.id   # 3
                            return redirect(Home)
                    else:
                        Error = 'Invalid Captcha !!'
                        return render(req, 'Login.html', context={'Err': Error, 'x': v})
                else:
                    Error = 'Auth User Not Found !!'
                    return render(req, 'Login.html', context={'Err': Error, 'x': v})
            else:
                Err = 'Password Does Not Match !!'
                return render(req, 'Login.html', context={'Err': Err, 'x': v})
        except:
            Err = 'Email Does Not Exists !!'
            return render(req, 'Login.html', context={'Err': Err, 'x': v})
    else:
        return render(req, 'Login.html', context={'x': v})


def Logout(req):
    logout(req)
    req.session.flush()
    return redirect(Login)


def DashBoard(req):
    Data = Users.objects.all().count()
    S = Users.objects.filter(Name__istartswith='a').count()
    return render(req, 'DashBoard.html', context={'x': Data, 'x1': S})


def DataTable(req):
    Data = Users.objects.filter(Role='user')
    X = Paginator(Data, 10)
    z = req.GET.get('page')
    a = X.get_page(z)
    return render(req, 'table.html', context={'user': a})


def Edit(req, id):
    Data = Users.objects.get(id=id)
    Auth = User.objects.get(username=Data.Email)
    if req.method == 'POST':
        nm = req.POST['ne']
        em = req.POST['em']
        Data.Email = em
        Data.Name = nm
        Auth.username = em
        Data.save()
        Auth.save()
        return redirect(DataTable)
    else:
        return render(req, 'Edit.html', context={'x': Data})


def Delete(req, user_id):
    Data = Users.objects.get(id=user_id)
    Auth = User.objects.get(username=Data.Email)
    Data.delete()
    Auth.delete()
    return redirect(DataTable)


def Forget(req, id):
    if req.method == 'POST' and 'em' in req.POST:
        em = req.POST.get('em', '')
        U = Users.objects.filter(Email=em).count() # 1, 0
        if U == 1:
            U2 = Users.objects.get(Email=em)  # admin@gmail.com
            id = U2.id       # 2
            OTP = random.randint(100000, 999999) # 1234454
            req.session['TP'] = OTP
            print(OTP)
            send_mail('Reset Password',
                      f'Your Otp is {OTP}',
                      settings.EMAIL_HOST_USER,
                      [em, ])
            red = redirect(f'/app1/Otp/{id}')
            red.set_cookie('Time', True, max_age=500)
            return red
        else:
            Error = 'Email Does Not Exists !!'
            return render(req, 'Forget.html', context={'Err': Error, 'x': id})
    return render(req, 'Forget.html', context={'x': id})


def Otp(req, id):
    if req.method == 'POST':
        if 'Otp' in req.POST and req.POST['Otp'] != '':
            if req.COOKIES.get('Time'):
                if 'pw' in req.POST and 'pw1' in req.POST:
                    password1 = req.POST['pw'] # 87
                    password2 = req.POST['pw1']
                    Otp_Sms = int(req.session.get('TP'))
                    if Otp_Sms == int(req.POST['Otp']):
                        if password1 and password2:
                            if password1 == password2:
                                try:
                                    U = Users.objects.get(id=id) # 2
                                    current = U.Password # 34
                                    if not check_password(password1, current):
                                        U.Password = make_password(password1)
                                        U.save()
                                        try:
                                            U1 = User.objects.get(username=U.Email)
                                            U1.password = make_password(password1)
                                            U1.save()
                                            del req.session['TP']
                                            return redirect(Login)
                                        except:
                                            Err = 'Auth User Not Found !!'
                                            return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                                    else:
                                        Err = '''You Can't Use Your Old Password'''
                                        return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                                except:
                                    Err = 'ID Not Found !!'
                                    return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                            else:
                                Err = 'Both Password Must Be Same !!'
                                return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                        else:
                            Err = 'Enter Some Values !!'
                            return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                    else:
                        Err = 'Otp Does Not Match !!'
                        return render(req, 'Otp.html', context={'Err': Err, 'x': id})
                else:
                    Err = 'Something Went Wrong !!'
                    return render(req, 'Otp.html', context={'Err': Err, 'x': id})
            else:
                Err = 'Your Otp Has Been Expire !!'
                return render(req, 'Otp.html', context={'Err': Err, 'x': id})
        else:
            Err = 'Something Went Wrong 1 !!'
            return render(req, 'Otp.html', context={'Err': Err, 'x': id})
    else:
        return render(req, 'Otp.html', context={'x': id})


async def Google_T(req):
    translated_text = None
    text = ''
    source_lang = 'auto'
    target_lang = 'en'
    if req.method == 'POST':
        text = req.POST.get('text')
        source_lang = req.POST.get('source_language', 'auto') # en
        target_lang = req.POST.get('target_language', 'en')  # hi
        if 'swap_languages' in req.POST:
            source_lang, target_lang = target_lang, source_lang
        translate = Translator()
        try:
            translator = await asyncio.to_thread(translate.translate, text, src=source_lang, dest=target_lang)
            translated_text = translator.text
        except Exception as e:
            return render(req, 'trans.html', context={'Err': str(e)})
    return render(req, 'trans.html', context={
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'translated_text': translated_text,
        'languages': L
    })


def Order(req):
    Data = Products.objects.all()
    return render(req, 'Order.html', context={'D': Data})


def Add_Product(req):
    if req.method == 'POST':
        n = req.POST['p_name']
        d = req.POST['p_ds']
        im = req.FILES['p_img']
        p = req.POST['p_pri']
        ob = Products(name=n, p_des=d, p_image=im, price=p)
        ob.save()
        return redirect(Order)
    else:
        return render(req, 'Add-Product.html')


def Display(req):
    Data = Products.objects.all()
    return render(req, 'product_display.html', context={'Data': Data})


def Cart(req):
    if req.method == 'POST':
        p_id = req.POST['product_id']
        user = req.session.get('U_id')
        if p_id and user:
            a = User_Products(userid=user, pr_id=p_id)
            a.save()
            return redirect(Display)
        else:
            return render(req, 'product_display.html', context={'Err': 'Product Id Not found'})
    else:
        return render(req, 'product_display.html')