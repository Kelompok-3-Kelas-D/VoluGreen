from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import transaction

from .models import OrganizationSubmission, Profile


User = get_user_model()


class ProfileSettingsForm(forms.Form):
    name = forms.CharField(max_length=150, label="Nama lengkap / organisasi")
    phone_number = forms.CharField(
        max_length=20, label="Nomor HP",
        validators=[RegexValidator(r"^\+?[0-9\s-]{9,20}$", "Masukkan nomor HP yang valid.")],
    )
    city = forms.CharField(max_length=100, label="Kota", required=False)
    organization_type = forms.ChoiceField(
        choices=Profile.OrganizationType.choices, label="Jenis organisasi", required=False,
    )
    organization_description = forms.CharField(
        label="Tentang organisasi", required=False, max_length=2000,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def __init__(self, *args, user, profile, submission=None, **kwargs):
        self.user = user
        self.profile = profile
        self.submission = submission
        initial = kwargs.pop("initial", {})
        initial.update({
            "name": profile.organization_name if profile.role == Profile.Role.ORGANIZER
            else (user.first_name or user.get_username()),
            "phone_number": profile.phone_number,
            "city": profile.city,
            "organization_type": profile.organization_type,
            "organization_description": submission.description if submission else "",
        })
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        if profile.role != Profile.Role.ORGANIZER:
            self.fields.pop("organization_type")
            self.fields.pop("organization_description")

    def clean(self):
        cleaned = super().clean()
        if self.profile.role == Profile.Role.ORGANIZER and not cleaned.get("organization_type"):
            self.add_error("organization_type", "Pilih jenis organisasi.")
        return cleaned


class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        initial=Profile.Role.VOLUNTEER,
        widget=forms.HiddenInput(attrs={"id": "r-role"}),
    )
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "id": "r-name",
                "autocomplete": "name",
                "placeholder": "Nama sesuai KTM/KTP",
            }
        ),
    )
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "id": "r-email",
                "autocomplete": "email",
                "placeholder": "nama@email.com",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s-]{9,20}$",
                message="Masukkan nomor HP yang valid, misalnya +62 812 3456 7890.",
            )
        ],
        widget=forms.TextInput(
            attrs={
                "id": "r-phone",
                "type": "tel",
                "autocomplete": "tel",
                "placeholder": "+62 8xx xxxx xxxx",
            }
        ),
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "id": "r-city",
                "autocomplete": "address-level2",
                "placeholder": "Contoh: Depok, Jawa Barat",
            }
        ),
    )
    organization_type = forms.ChoiceField(
        choices=Profile.OrganizationType.choices,
        required=False,
        widget=forms.Select(attrs={"id": "r-type"}),
    )
    organization_description = forms.CharField(
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={
            "id": "r-org-description", "rows": 3,
            "placeholder": "Ceritakan kegiatan atau fokus organisasi secara singkat.",
        }),
    )
    terms = forms.BooleanField(
        error_messages={
            "required": "Kamu harus menyetujui Syarat & Ketentuan untuk mendaftar."
        },
        widget=forms.CheckboxInput(attrs={"id": "r-terms"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {
                "id": "r-pass",
                "autocomplete": "new-password",
                "placeholder": "Minimal 8 karakter",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "id": "r-pass2",
                "autocomplete": "new-password",
                "placeholder": "Ulangi kata sandi",
            }
        )

    def clean_username(self):
        email = self.cleaned_data["username"].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError("Email ini sudah terdaftar.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        if role == Profile.Role.VOLUNTEER and not cleaned_data.get("city"):
            self.add_error("city", "Kota domisili wajib diisi untuk relawan.")

        if role == Profile.Role.ORGANIZER and not cleaned_data.get(
            "organization_type"
        ):
            self.add_error(
                "organization_type",
                "Jenis organisasi wajib dipilih untuk penyelenggara.",
            )

        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["username"]
        role = self.cleaned_data["role"]
        name = self.cleaned_data["name"].strip()

        user.username = email
        user.email = email
        user.first_name = name if role == Profile.Role.VOLUNTEER else ""

        if not commit:
            return user

        user.save()
        profile = Profile.objects.create(
            user=user,
            role=role,
            phone_number=self.cleaned_data["phone_number"],
            city=self.cleaned_data.get("city", ""),
            organization_name=name if role == Profile.Role.ORGANIZER else "",
            organization_type=self.cleaned_data.get("organization_type", "")
            if role == Profile.Role.ORGANIZER
            else "",
        )
        if role == Profile.Role.ORGANIZER:
            OrganizationSubmission.objects.get_or_create(
                contact_email=email,
                defaults={
                    "name": profile.organization_name,
                    "type": profile.get_organization_type_display(),
                    "city": profile.city,
                    "description": self.cleaned_data.get("organization_description", "").strip(),
                    "status": OrganizationSubmission.Status.PENDING,
                },
            )
        return user


class LoginForm(AuthenticationForm):
    role = forms.ChoiceField(
        choices=Profile.Role.choices,
        initial=Profile.Role.VOLUNTEER,
        required=False,
        widget=forms.HiddenInput(attrs={"id": "login-role-value"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {
                "id": "l-email",
                "autocomplete": "username",
                "placeholder": "Masukkan email",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "id": "l-pass",
                "autocomplete": "current-password",
                "placeholder": "Minimal 8 karakter",
            }
        )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_staff or user.is_superuser:
            return
        selected_role = self.cleaned_data.get("role")

        # Form login cepat di beranda tidak meminta pengguna memilih peran.
        # Dalam kasus itu, peran diambil otomatis dari profil akun.
        if not selected_role:
            return

        profile = getattr(user, "profile", None)
        if profile is None or profile.role != selected_role:
            raise ValidationError(
                "Peran yang dipilih tidak sesuai dengan akun ini.",
                code="invalid_role",
            )
