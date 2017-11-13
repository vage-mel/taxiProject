# django
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect
from django.core.context_processors import csrf
from django.db.models import Q
from django.utils.formats import localize
from django.core.urlresolvers import reverse
from django.db import transaction

# python
import datetime
import json
import hashlib
from enum import Enum

# app
from taxiProject.redis_connection import redis_conn
from .models import Order, Car, User
from .forms import UserChangeForm, FormCreateOrder, CommentCreationForm, CarChangeForm


class Status(Enum):
    find = 1
    in_process = 2
    complete = 3
    canceled_person = 4
    canceled_driver = 5


def _paginator(obj_list, page, page_num):
    paginator = Paginator(obj_list, page_num)

    try:
        obj_list = paginator.page(page)
    except PageNotAnInteger:
        obj_list = paginator.page(1)
    except EmptyPage:
        obj_list = paginator.page(paginator.num_pages)

    return obj_list


def home(request):
    if request.user.is_authenticated():
        user = request.user

        if not user.is_driver:
            return HttpResponseRedirect(reverse('person:create_order'))
        else:
            return HttpResponseRedirect(reverse('driver:list_orders'))
    else:
        return HttpResponse(get_template('home.html').render())


# пользователь авторизован
def auths(func):
    def wrapper_func(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            return HttpResponse(get_template('error.html').render({
                'ErrorText': 'Вы не авторизованы'
            }))

        if user.is_authenticated() and not user.phone_number:
            return redirect('/auth/register/reg_phone/')

        return func(request, *args, **kwargs)

    return wrapper_func


# пользователь в режиме "водитель"
def is_driver(func):
    def wrapper_func(request, *args, **kwargs):
        user = request.user
        car = Car.objects.filter(user=user)

        if not car.exists():
            return HttpResponse(get_template('error.html').render({
                'ErrorText': 'У вас нет машины',
                'user': user
            }))

        if not user.is_driver:
            return HttpResponse(get_template('error.html').render({
                'ErrorText': 'Вы в режиме пользователя',
                'user': user
            }))

        return func(request, *args, **kwargs)

    return wrapper_func


# пользователь в режиме "пользователь"
def is_user(func):
    def wrapper_func(request, *args, **kwargs):
        user = request.user

        if user.is_driver:
            return HttpResponse(get_template('error.html').render({
                'ErrorText': 'Вы в режиме водителя',
                'user': user
            }))
        
        return func(request, *args, **kwargs)

    return wrapper_func


@auths
def in_person(request):
    user = request.user

    if not user.is_driver:
        return HttpResponse(get_template('error.html').render({
            'ErrorText': 'Вы в режиме пользователя',
            'user': user
        }))

    if Order.objects.filter(status=Status.in_process.value, driver=user):
        return HttpResponse(get_template('error.html').render({
            'ErrorText': 'Завершите заказы',
            'user': user
        }))
    
    user.is_driver = False
    user.save()
    return HttpResponseRedirect(reverse('person:create_order'))


@auths
def in_driver(request):
    user = request.user

    car = Car.objects.filter(user=user)

    if not car.exists():
        return HttpResponse(get_template('error.html').render({
            'ErrorText': 'Вы не имеете машину',
            'user': user,
        }))

    if user.is_driver:
        return HttpResponse(get_template('error.html').render({
            'ErrorText': 'Вы в режиме водителя',
            'user': user
        }))

    orders = Order.objects.filter(Q(status=Status.in_process.value) |
                                  Q(status=Status.find.value),
                                  user=user)
    if orders.exists():
        return HttpResponse(get_template('error.html').render({
            'ErrorText': 'Дождитесь оконачания выполнения заказов',
            'user': user,
        }))

    user.is_driver = True
    user.save()
    return HttpResponseRedirect(reverse('driver:list_orders'))


@auths
@is_user
def person_create_order(request):
    user = request.user
    form = FormCreateOrder(request.POST or None)
    in_template = {
        'form': form,
        'user': user
    }
    in_template.update(csrf(request))

    if not form.is_valid():
        return HttpResponse(get_template('person/create_order.html').render(in_template))
    else:
        order = Order(user=user,
                      From=form.cleaned_data['From'],
                      to=form.cleaned_data['to'],
                      cost=form.cleaned_data['cost'],
                      info_order=form.cleaned_data['info_order'],
                      status=Status.find.value,
                      date=datetime.datetime.now()
                      )
        order.save()

        response_data = {
            'order': {
                'id': order.pk,
                'dateStr':  localize(order.date),
                'date': str(order.date),
                'From': order.From,
                'to': order.to,
                'cost': order.cost,
                'infoOrder': order.info_order,
            },
            'user': {
                'id': request.user.pk,
                'firstName': user.first_name,
            },
            'action': 'create'
        }

        redis_conn.publish('publish_channel', json.dumps(response_data))

        return HttpResponseRedirect(reverse('person:current_orders'))


def _rating_calculate(orders):
    count = 0
    rating = 0
    for order in orders:
        if order.rating:
            rating += order.rating
            count += 1

    if count != 0:
        rating /= count

    return rating


@auths
def profile_info(request, user_id):
    rating = 0
    user = request.user
    in_template = {
        'user': user,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    if user.id == int(user_id):
        in_template.update({
            'user_profile': user,
            'is_edit_mode': True
        })
    else:
        in_template.update({
            'user_profile': get_object_or_404(User, pk=user_id),
            'is_edit_mode': False
        })

    car = Car.objects.filter(user=in_template['user_profile'])

    if car.exists():
        orders_with_comment = Order.objects.filter(driver=in_template['user_profile']).exclude(comment="").order_by('-date')[:5]

        orders = Order.objects.filter(driver=in_template['user_profile'])

        if orders.exists():
            rating = _rating_calculate(orders)

        in_template.update({
            'orders_with_comment': orders_with_comment,
            'rating': rating
        })

    return HttpResponse(get_template('profile_info.html').render(in_template))


@auths
def profile_edit(request):
    user = request.user

    in_template = {
        'user': user,
        'person_id': user.pk,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    in_template.update(csrf(request))
    user_сhange_form = UserChangeForm(request.POST or None, instance=request.user)
    in_template.update({'form': user_сhange_form})

    if request.method == 'POST':
        if user_сhange_form.is_valid():
            user_сhange_form.save()

            if user_сhange_form.cleaned_data['password']:
                user = auth.authenticate(username=user.phone_number,
                                         password=user_сhange_form.cleaned_data['password'])
                auth.login(request, user)

            return HttpResponseRedirect(reverse('profile_info', kwargs={'user_id': user.id}))

    return HttpResponse(get_template('profile_edit.html').render(in_template))


@auths
@is_user
def person_current_orders(request):
    user = request.user

    orders = Order.objects.filter(Q(status=Status.in_process.value) |
                                  Q(status=Status.find.value) |
                                  Q(status=Status.canceled_driver.value),
                                  user__city=user.city,
                                  user=user).order_by('-status', '-date')

    orders = _paginator(orders, request.GET.get('page'), 10)
    token = request.session.session_key

    in_template = {
        'user': user,
        'canceled_driver': Status.canceled_driver,
        'orders': orders,
        'token': token
    }

    return HttpResponse(get_template('person/current_orders.html').render(in_template))


@auths
@is_user
def person_info_order(request, order_id):
    user = request.user
    order = Order.objects.get(pk=order_id, user=user)

    in_template = {
        'user': user,
        'order': order
    }

    return HttpResponse(get_template('person/info_order.html').render(in_template))


@auths
@is_user
def person_history_orders(request):
    user = request.user
    comment_creation_form = CommentCreationForm(request.POST or None)

    if request.method == 'GET':
        orders = Order.objects.filter(Q(status=Status.complete.value) |
                                      Q(status=Status.canceled_person.value) |
                                      Q(status=Status.canceled_driver.value),
                                      user=user,
                                      user__city=user.city
                                      ).order_by('-date')

        orders = _paginator(orders, request.GET.get('page'), 10)

        in_template = {
            'user': user,
            'orders': orders,
            'comment_creation_form': comment_creation_form
        }

        in_template.update(csrf(request))

        return HttpResponse(get_template('person/history_orders.html').render(in_template))
    else:
        order = get_object_or_404(Order, pk=int(request.POST['order_id']), user=user)

        order.comment = request.POST['text']
        order.rating = request.POST['order_rating']
        order.save()
        return HttpResponse(json.dumps({'order_id': request.POST['order_id']}), content_type='application/js')


@auths
@is_driver
def driver_history_orders(request):
    user = request.user
    orders_list = Order.objects.filter(Q(status=Status.complete.value) |
                                       Q(status=Status.canceled_person.value) |
                                       Q(status=Status.canceled_driver.value),
                                       driver=user).order_by('-date')

    orders = _paginator(orders_list, request.GET.get('page'), 10)

    in_template = {
        'user': user,
        'orders': orders,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    return HttpResponse(get_template('driver/history_orders.html').render(in_template))


@auths
@is_driver
def driver_list_orders(request):
    user = request.user
    orders = Order.objects.filter(status=Status.find.value,
                                  user__city=user.city).exclude(user=user).order_by('-date')

    orders = _paginator(orders, request.GET.get('page'), 10)
    token = request.session.session_key

    in_template = {
        'user': user,
        'orders': orders,
        'access': True,
        'token': token,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    in_template.update(csrf(request))
    return HttpResponse(get_template('driver/list_orders.html').render(in_template))


@auths
@is_driver
def driver_perform_order_ajax(request):
    if request.POST.get('orderPk'):
        user = request.user
        response_dict = {}
        orders = Order.objects.filter(user__city=user.city,
                                      driver=user,
                                      status=Status.in_process.value)
        if orders.exists():
            response_dict.update({'access_': False})
        else:
            with transaction.atomic():
                order = get_object_or_404(Order.objects.select_for_update(), pk=request.POST.get('orderPk'))

                if order.status == Status.find.value:
                    order.status = Status.in_process.value
                    order.driver = user
                    order.save()
                    response_dict.update({'access_': True})

                    profile_hash_str = hashlib.sha1(str(order.user.pk).encode('utf-8')).hexdigest()

                    response_data = {
                        'driver': {
                            'id': order.driver.pk,
                            'first_name': order.driver.first_name,
                            'phone_number': order.driver.phone_number
                        },
                        'order': {
                            'id': order.pk
                        },
                        'action': 'proccess'
                    }
                    redis_conn.publish('private_%s' % profile_hash_str, json.dumps(response_data))

                    response_data = {
                        'order': {
                            'id': order.pk
                        },
                        'action': 'delete'
                    }
                    redis_conn.publish('publish_channel', json.dumps(response_data))

        request.session['driver_geo_active'] = 1

        return HttpResponse(json.dumps(response_dict), content_type='application/js')
    else:
        return HttpResponse(get_template('error.html').render({'ErrorText': 'Ошибка'}))


@auths
@is_driver
def driver_current_orders(request):
    user = request.user

    orders = Order.objects.filter(Q(status=Status.in_process.value) |
                                  Q(status=Status.canceled_person.value),
                                  user__city=user.city,
                                  driver=user).exclude(user=user).order_by('-status', '-date')

    token = request.session.session_key

    in_template = {
        'user': user,
        'orders': orders,
        'canceled_person': Status.canceled_person,
        'token': token,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    return HttpResponse(get_template('driver/current_orders.html').render(in_template))


@auths
@is_driver
def complete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, driver=request.user)
    order.status = Status.complete.value
    order.save()

    profile_hash_str = hashlib.sha1(str(order.user.pk).encode('utf-8')).hexdigest()

    request.session['driver_geo_active'] = 0

    response_data = {
        'order': {
            'id': order.id,
            'status': Order.STATUS[2][1]
        },
        'action': 'complete'
    }

    redis_conn.publish('private_%s' % profile_hash_str, json.dumps(response_data))

    return HttpResponseRedirect(reverse('driver:current_orders'))


@auths
def cancel_order(request, order_id):
    user = request.user

    if not user.is_driver:
        order = get_object_or_404(Order, pk=order_id, user=user)

        if order.driver and order.status == Status.in_process.value:
            profile_hash_str = hashlib.sha1(str(order.driver.pk).encode('utf-8')).hexdigest()

            response_data = {
                'order': {
                    'id': order.id,
                    'status': Order.STATUS[3][1]
                },
                'action': 'cancel'
            }

            redis_conn.publish('private_%s' % profile_hash_str, json.dumps(response_data))
            order.status = Status.canceled_person.value
            order.save()

        elif order.status == Status.find.value:
            response_data = {
                'order': {
                    'id': order.pk
                },
                'action': 'delete'
            }
            redis_conn.publish('publish_channel', json.dumps(response_data))

            order.delete()

        return HttpResponseRedirect(reverse('person:current_orders'))

    elif user.is_driver:
        order = get_object_or_404(Order, pk=order_id, driver=user)

        if order.status == Status.in_process.value:
            order.status = Status.canceled_driver.value
            order.save()

            profile_hash_str = hashlib.sha1(str(order.user.pk).encode('utf-8')).hexdigest()
            request.session['driver_geo_active'] = 0
            response_data = {
                'order': {
                    'id': order.pk,
                    'status': Order.STATUS[4][1]
                },
                'action': 'cancel'
            }

            redis_conn.publish('private_%s' % profile_hash_str, json.dumps(response_data))

        return HttpResponseRedirect(reverse('driver:current_orders'))


@auths
def close_order(request, order_id):

    if request.user.is_driver:
        order = get_object_or_404(Order, pk=order_id, driver=request.user)

        if order.status == Status.canceled_person.value:
            order.status = Status.complete.value
            order.save()

    elif not request.user.is_driver:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        if order.status == Status.canceled_driver.value:
            order.status = Status.complete.value
            order.save()

    if request.user.is_driver:
        return HttpResponseRedirect(reverse('driver:current_orders'))
    else:
        return HttpResponseRedirect(reverse('person:current_orders'))


@auths
@is_driver
def car_edit(request):
    user = request.user
    user_car = Car.objects.get(user=user)
    car_creation_form = CarChangeForm(request.POST or None, instance=user_car)

    in_template = {
        'user': request.user,
        'car_creation_form': car_creation_form,
        'driver_geo_active': request.session.get('driver_geo_active')
    }

    in_template.update(csrf(request))

    if request.method == 'POST':
        if car_creation_form.is_valid():
            car_creation_form.save()
            return HttpResponseRedirect(reverse('profile_info', kwargs={'user_id': user.id}))

    return HttpResponse(get_template('driver/car_edit.html').render(in_template))


@auths
def geo_send_position_ajax(request):
    user = request.user
    order = Order.objects.get(driver=user, status=Status.in_process.value)

    profile_hash_str = hashlib.sha1(str(order.user.pk).encode('utf-8')).hexdigest()

    request_data = json.loads(request.POST.get('data'))

    response_data = {
        'order': {
            'id': order.pk
        },
        'action': 'moveCoordinates',
        'coordinates': request_data['coordinates']
    }
    redis_conn.publish('private_%s' % profile_hash_str, json.dumps(response_data))

    response = {
        'isSend': True
    }

    return HttpResponse(json.dumps(response), content_type='application/json')

# @auths
# def geo_access_ajax(request):
#    user = request.user
#    is_geo_access = request.POST.get('isGeoAccess')
#    user.is_geo_access = is_geo_access
#    user.save();
#    response = {
#        'isGeoAccess': user.is_geo_access
#    }
#    return HttpResponse(json.dumps(response), content_type='application/js')

