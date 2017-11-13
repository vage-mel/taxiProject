# django
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template.loader import get_template
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

# python
import json
import random
import re
import requests

# app
from apps.your_taxi.forms import UserCreationForm, CarCreationForm, DriverCreationForm
from apps.your_taxi.models import Car, User
from taxiProject import settings


def login(request):
    args = {}
    args.update(csrf(request))
    if not request.user.is_authenticated():
        if request.POST:
            phone_number = request.POST.get('phone_number', '')
            password = request.POST.get('password', '')
            phone_number = _get_normal_phone_number(phone_number)

            try:
                user = auth.authenticate(id=User.objects.get(phone_number=phone_number).id, password=password)
                auth.login(request, user)
                return redirect('/')
            except:
                args['login_error'] = 'пользователь не найден'
                return render_to_response('login.html', args)
        else:
            return render_to_response('login.html', args)
    else:
        return redirect('/')


def logout(request):
    if not request.user.phone_number:
        try:
            del request.session['pin_sended']
            del request.session['phone_number']
        except KeyError:
            pass
        request.user.delete()

    auth.logout(request)
    return redirect('/auth/login/')


def register(request, reg_mode='user'):
    user = request.user

    if user.is_authenticated() and user.phone_number:
            return redirect('/')

    args = {
        'reg_mode': reg_mode
    }
    args.update(csrf(request))

    if not user.is_authenticated() and reg_mode in ('user', 'driver'):
        if reg_mode == 'user':
            form = UserCreationForm(request.POST or None, auto_id='signup-%s')
            args['form'] = form

            if not form.is_valid():
                return HttpResponse(get_template("register.html").render(args))

        elif reg_mode == 'driver':
            form = DriverCreationForm(request.POST or None, auto_id='signup-%s')
            car_creation_form = CarCreationForm(request.POST or None, auto_id='car-%s')

            args['form'] = form
            args['car_creation_form'] = car_creation_form

            if not form.is_valid() or not car_creation_form.is_valid():
                return HttpResponse(get_template("register.html").render(args))

        id = form.save().pk
        new_user = auth.authenticate(id=id, password=form.cleaned_data['password'])
        auth.login(request, new_user)

        if reg_mode == 'driver':
            car = car_creation_form.save(commit=False)
            car.user = new_user
            car.save()

            new_user.is_driver = True
            new_user.save()

    elif reg_mode == 'reg_phone':
        in_template = {
            'user': request.user,
            'reg_mode': reg_mode,
        }
        in_template.update(csrf(request))

        if request.session.get('pin_sended'):
            in_template['pin_sended'] = True

            if request.method == 'POST':
                pin = request.POST.get("pin", "")
                phone_number = request.POST.get("phone_number", "")

                try:
                    pin = int(pin)
                except ValueError:
                    pin = 0

                if _verify_pin(get_normal_phone_number(phone_number), pin):
                    try:
                        del request.session['pin_sended']
                        del request.session['phone_number']
                        cache.delete(phone_number)
                    except KeyError:
                        pass

                    user.phone_number = get_normal_phone_number(phone_number)
                    user.save()

                    return redirect('/')
                else:
                    in_template['phone_number'] = phone_number
                    in_template['error_message'] = 'Неверный код. Пожалуйста, введите код, который ' \
                                                   'Вы только что получили. '
            else:
                in_template['phone_number'] = request.session.get('phone_number')

        return HttpResponse(get_template("register.html").render(in_template))

    return redirect('/auth/register/reg_phone/')


def register_car(request):
    user = request.user

    if not user.is_authenticated() or not user.phone_number:
        return redirect("/auth/register/")

    car = Car.objects.filter(user=user)

    if car.exists():
        return redirect('/')

    args = {}
    args.update(csrf(request))
    car_creation_form = CarCreationForm(request.POST or None)

    if not car_creation_form.is_valid():
        args['car_creation_form'] = car_creation_form
        return HttpResponse(get_template("registerCar.html").render(args))

    car = car_creation_form.save(commit=False)
    car.user = user
    car.save()

    user.is_driver = True
    user.save()

    return redirect('/')


def _get_pin(length=5):
    return random.sample(range(10**(length-1), 10**length), 1)[0]


def _verify_pin(phone_number, pin):
    return pin == cache.get(phone_number)


def _get_normal_phone_number(phone_number):

    if len(phone_number) == 11:
        phone_number = phone_number[1:]

    if len(phone_number) == 12:
        phone_number = phone_number[2:]

    return phone_number


def ajax_send_pin(request):
    user = request.user
    response = {}

    if not user.is_authenticated() or user.is_authenticated() and user.phone_number:
        return HttpResponse("Ошибка доступа", content_type='text/plain', status=500)

    phone_number = request.POST.get('phone_number', "").strip()
    result = re.match(r'^(?:\+79|89|79){1}[0-9]{9}$', phone_number)

    # валидация номера
    if not result:
        response['message'] = 'Некорректный мобильный номер. Необходимо корректно ввести номер. Например: +79210000007'
        response['success'] = False
        return HttpResponse(json.dumps(response), content_type='application/js')

    # проверка на наличие номера в базе
    try:
        User.objects.get(phone_number=_get_normal_phone_number(phone_number))
        response['message'] = 'Данный номер уже зарегестрирован, укажите другой.'
        response['success'] = False
        return HttpResponse(json.dumps(response), content_type='application/json')
    except ObjectDoesNotExist:
        pass

    pin = _get_pin()

    cache.set(_get_normal_phone_number(phone_number), pin, 3600)
    try:
        url = settings.SMS_RU_URL
        requests.get(url.format(phone_number, pin))
        response['success'] = True
        request.session['pin_sended'] = True
        request.session['phone_number'] = phone_number
    except:
        response['success'] = False
        response['message'] = 'Ошибка отправки смс'

    return HttpResponse(json.dumps(response), content_type='application/json')