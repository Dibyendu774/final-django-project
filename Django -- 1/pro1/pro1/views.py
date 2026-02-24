from django.shortcuts import render, redirect
from django.http import HttpResponse
from app1.models import Users
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login


def Button(req):
    if req.method == 'POST':
        em = req.POST['ema']
        pw = req.POST['pwd']
        try:
            Record = Users.objects.get(Email=em) # normal table
            if check_password(pw, Record.Password):  # normal table
                u1 = authenticate(username=em, password=pw) # Auth_user
                if u1 is not None:
                    if Record.Role == 'Admin':
                        login(req, u1)
                        return redirect('/app1/')
                    else:
                        return HttpResponse('Failed to Load App2')
                else:
                    Err = 'Auth User Not Found !!'
                    return render(req, 'button.html', context={'Err': Err})
            else:
                Err = 'Password Does Not Match !!'
                return render(req, 'button.html', context={'Err': Err})
        except:
            Err = 'Email Does Not Found !!'
            return render(req, 'button.html', context={'Err': Err})
    else:
        return render(req, 'Button.html')