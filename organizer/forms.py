from django import forms

from main.models import Category

from .models import DampakKegiatan, Kegiatan


class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = (
            "nama", "deskripsi", "kategori", "tanggal_mulai", "nama_lokasi",
            "alamat", "kota", "latitude", "longitude", "kuota",
        )
        widgets = {
            "deskripsi": forms.Textarea(attrs={"rows": 4}),
            "tanggal_mulai": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "kuota": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kategori"].queryset = Category.objects.filter(is_active=True)
        self.fields["kategori"].empty_label = "Pilih kategori"
        self.fields["tanggal_mulai"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["latitude"].required = False
        self.fields["longitude"].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "organizer-input")

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get("latitude") is None) != (cleaned.get("longitude") is None):
            raise forms.ValidationError("Isi latitude dan longitude bersama-sama, atau kosongkan keduanya.")
        return cleaned


class DampakForm(forms.ModelForm):
    class Meta:
        model = DampakKegiatan
        fields = ("sampah_terkumpul_kg", "pohon_ditanam", "area_dibersihkan_m2", "catatan")
        widgets = {
            "sampah_terkumpul_kg": forms.NumberInput(attrs={"min": 0, "step": "0.01"}),
            "pohon_ditanam": forms.NumberInput(attrs={"min": 0}),
            "area_dibersihkan_m2": forms.NumberInput(attrs={"min": 0}),
            "catatan": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "organizer-input")
