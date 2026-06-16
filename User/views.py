from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import GoldPrice

# Home Page
def index(request):
    return render(request, "index.html")


# Register
def register(request):
    if request.method == "POST":

        first = request.POST.get('fname')
        last = request.POST.get('lname')
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        psw = request.POST.get('psw')
        psw1 = request.POST.get('psw1')

        if psw == psw1:

            if User.objects.filter(username=uname).exists():
                messages.info(request, "Username already exists")
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already exists")
                return redirect('register')

            else:
                user = User.objects.create_user(
                    username=uname,
                    email=email,
                    password=psw,
                    first_name=first,
                    last_name=last
                )

                user.save()

                messages.success(request, "Registration Successful")
                return redirect('login')

        else:
            messages.error(request, "Passwords do not match")
            return redirect('register')

    return render(request, "register.html")


# Login
def login(request):

    if request.method == "POST":

        uname = request.POST.get('uname')
        psw = request.POST.get('psw')

        user = auth.authenticate(
            username=uname,
            password=psw
        )

        if user is not None:

            auth.login(request, user)

            return redirect('data')

        else:

            messages.error(request, "Invalid Username or Password")
            return redirect('login')

    return render(request, "login.html")


# Prediction Page
def data(request):

    if request.method == "POST":

        try:

            spx = float(request.POST.get('spx'))
            uso = float(request.POST.get('uso'))
            slv = float(request.POST.get('slv'))
            eur = float(request.POST.get('eur'))

            import pandas as pd
            from sklearn.ensemble import RandomForestRegressor

            gold_data = pd.read_csv(
                "static/gld_price_data.csv"
            )

            X = gold_data.drop(
                ['Date', 'GLD'],
                axis=1
            )

            Y = gold_data['GLD']

            model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )

            model.fit(X, Y)

            prediction = float(
                model.predict(
                    [[spx, uso, slv, eur]]
                )[0]
            )

            GoldPrice.objects.create(
                SPX=spx,
                USO=uso,
                SLV=slv,
                EUR_USD=eur,
                GOLD=prediction
            )

            return render(
                request,
                "predict.html",
                {
                    "spx": spx,
                    "uso": uso,
                    "slv": slv,
                    "eur": eur,
                    "price": round(prediction, 2)
                }
            )

        except Exception as e:

            return render(
                request,
                "data.html",
                {
                    "error": str(e)
                }
            )

    return render(request, "data.html")


# Result Page
def predict(request):
    return render(request, "predict.html")


# Contact Page
def contact(request):
    return render(request, "contact.html")


# Logout
def logout(request):
    auth.logout(request)
    return redirect('/')