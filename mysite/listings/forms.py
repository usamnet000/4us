from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from .validators import CustomPasswortValidator,CommonPasswordValidator

CITY_CHOICES = (
    ('Omran', 'عمران'),
    ('AlBayda', 'البيضاء'),
    ('Hodeidah', 'الحديدة'),
    ('Hollow', 'الجوف'),
    ('AlMahweet', 'المحويت'),
    ('Dhamar', 'ذمار'),
    ('Hajjah', 'حجة'),
    ('Ibb', 'إب'),
    ('Marib', 'مأرب'),
    ('Rima', 'ريمة'),
    ('Sa\'ada', 'صعدة'),
    ('Sana\'a', 'صنعاء'),
    ('Taiz', 'تعز'),
    ('Aden', 'عدن'),
    ('Abyan', 'أبين'),
    ('Dali', 'الضالع'),
    ('ALamrah', 'المهرة'),
    ('Hadramout', 'حضرموت'),
    ('Socotra', 'سقطرى'),
    ('Lahj', 'لحج'),
    ('Shabwah', 'شبوة'),
)
UNIT_TYPE_CHOICES = (
  (1, 'متر مربع'),
  (2, 'قدم مربع'),
  (3, "فدان"),
)

class AddressForm(forms.Form):
    address = forms.CharField(required=False, max_length=100)
    latitude = forms.DecimalField(required=True)
    longitude = forms.DecimalField(required=True)
    city_option = forms.ChoiceField(widget=forms.Select, choices=CITY_CHOICES, required=False)



class RegisterForm(UserCreationForm):
    username =forms.EmailField(label='البريد الالكتروني', widget=forms.EmailInput(
                    attrs={
                        "class": "form-control",
                        "placeholder": "البريد الإلكتروني"
                    }
                    ))

    password1 = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput(
        attrs={
            'onkeyup': "validatePassword(this.value);",
            "placeholder": "كلمة المرور"
        }
    ) ,validators=[CustomPasswortValidator],help_text=
    """
     كلمة المرور لا يمكن ان تكون مشابه للمعلومات الشخصية
     <br/>
      كلمة المرور قصيرة يجب ان تحتوي على الأقل 8 حرف.
    <br/>
    كلمة المرور لا يمكن ان تكون شائعة الاستخدام
    <br/>
     كلمة المرور لا يمكن تكون عدد ككل
     <br/>
    """ )
    password2 = forms.CharField(label='تأكيد كلمة المرور', widget=forms.PasswordInput(
        attrs={
            "placeholder": "تأكيد كلمة المرور"
        }),help_text="إدخل نفس كلمة المرور كما  سبق. للتحقق")

    class Meta:
        model = User
        fields = ("username",
                  'password1',
                  'password2'
                  )

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("البريد الإلكتروني موجود ")
        return username



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("كلمة المرور غير متطابقة")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['username'],
            self.cleaned_data['password1']
        )
        user.active = True
        user.staff = False
        user.save()

        return user


class EditProfileForm(forms.Form):
    city = forms.ChoiceField(widget=forms.Select, choices=CITY_CHOICES, required=False)

class UnitForm(forms.Form):
    unit_option = forms.ChoiceField(widget=forms.Select, choices=UNIT_TYPE_CHOICES, required=False)