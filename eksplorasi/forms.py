from django import forms

from .models import KoleksiKegiatan


class KoleksiForm(forms.ModelForm):
    class Meta:
        model = KoleksiKegiatan
        fields = ["nama", "catatan"]
        widgets = {
            "nama": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Contoh: Rencana akhir pekan"}
            ),
            "catatan": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Catatan (opsional)"}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_nama(self):
        nama = self.cleaned_data["nama"].strip()
        if not nama:
            raise forms.ValidationError("Nama koleksi tidak boleh kosong.")
        duplikat = KoleksiKegiatan.objects.filter(pengguna=self.user, nama__iexact=nama)
        if self.instance.pk:
            duplikat = duplikat.exclude(pk=self.instance.pk)
        if duplikat.exists():
            raise forms.ValidationError("Kamu sudah punya koleksi dengan nama ini.")
        return nama