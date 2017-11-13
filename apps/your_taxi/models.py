from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager, PermissionsMixin

SEX = (
    ('М', 'Мужской'),
    ('Ж', 'Женский')
)


class City(models.Model):
    name = models.CharField('Город', max_length=30)

    def __str__(self):
        return str(self.name)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, email,
                     first_name, last_name,
                     date_of_birth, city, sex, password,
                     is_staff, is_superuser, **extra_fields):

        if not phone_number:
            raise ValueError('The given phone number must be set')

        user = self.model(phone_number=phone_number, email=email,
                          first_name=first_name, last_name=last_name,
                          date_of_birth=date_of_birth, city=city,
                          sex=sex, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email,
                    first_name, last_name,
                    date_of_birth, city, sex,
                    password=None, **extra_fields):
        return self._create_user(phone_number, email,
                                 first_name, last_name,
                                 date_of_birth, city, sex,
                                 password, False, False, **extra_fields)

    def create_superuser(self, phone_number, email,
                         first_name, last_name,
                         date_of_birth, city, sex,
                         password, **extra_fields):
        return self._create_user(phone_number, email,
                                 first_name,last_name,
                                 date_of_birth, city, sex,
                                 password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    GEO_ACCESS = (
        (1, 'Разрешено'),
        (2, 'Запрещено')
    )

    email = models.EmailField('E-mail адрес', max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=30)
    phone_number = models.CharField('Телефон', max_length=10)
    date_of_birth = models.DateField('Дата рождения', null=True)
    city = models.ForeignKey(City)
    #is_geo_access = models.IntegerField(choices=GEO_ACCESS)
    sex = models.CharField('Пол', max_length=3, choices=SEX, null=True)
    is_driver = models.BooleanField('Режим водителя', default=False)
    is_staff = models.BooleanField(_('staff status'),
                                   default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))

    is_active = models.BooleanField(_('active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'date_of_birth', 'city', 'sex']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return str(self.first_name + ' ' + self.last_name)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class Car(models.Model):
    number = models.CharField('Номер', unique=True, max_length=10)
    mark = models.CharField('Марка', max_length=20)
    model = models.CharField('Модель', max_length=20)
    year_issue = models.IntegerField('Год выпуска')
    color = models.CharField('Цвет', max_length=15)
    user = models.OneToOneField(User)

    def __str__(self):
        return str(self.mark + self.model)


class Order(models.Model):

    def __str__(self):
        return str(self.date) + " " + self.user.first_name + " " + str(self.cost)

    STATUS = (
        (1, 'Поиск'),
        (2, 'В процессе'),
        (3, 'Завершен'),
        (4, 'Отменен пользователем'),
        (5, 'Отменен водителем')
    )

    user = models.ForeignKey(User, related_name='orders_passenger')
    driver = models.ForeignKey(User, related_name='orders_driver', null=True, blank=True)

    From = models.CharField(max_length=50)
    to = models.CharField(max_length=50)
    cost = models.IntegerField()
    date = models.DateTimeField()

    status = models.IntegerField(choices=STATUS)
    info_order = models.CharField(max_length=100)
    comment = models.CharField(max_length=100)
    rating = models.IntegerField(null=True, blank=True)
    passenger_count = models.IntegerField(default=1)