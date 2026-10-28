# =====================================================================
# === START BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ======
# =====================================================================
import re

from django import forms
from django.core.exceptions import ValidationError

from .models import (
    PESAN_DUPLIKAT,
    PendaftaranRelawan,
    StatusPendaftaran,
    alasan_tidak_bisa_mendaftar,
)

POLA_TELEPON = re.compile(r"^\+?[\d\s().-]{8,30}$")


class _ValidasiInformasiPendaftaranMixin:
    """Validasi bersama untuk field informasi pendaftaran relawan."""

    def clean_motivasi(self):
        motivasi = (self.cleaned_data.get("motivasi") or "").strip()
        if not motivasi:
            raise ValidationError("Motivasi mengikuti kegiatan wajib diisi.")
        if len(motivasi) < 10:
            raise ValidationError("Motivasi minimal terdiri dari 10 karakter.")
        return motivasi

    def clean_kontak_darurat(self):
        kontak = (self.cleaned_data.get("kontak_darurat") or "").strip()
        if not kontak:
            raise ValidationError("Kontak darurat wajib diisi.")
        if len(kontak) < 8:
            raise ValidationError("Kontak darurat minimal terdiri dari 8 karakter.")
        hanya_angka = re.sub(r"\D", "", kontak)
        if not POLA_TELEPON.match(kontak) or len(hanya_angka) < 8 or len(hanya_angka) > 16:
            raise ValidationError(
                "Masukkan nomor telepon kontak darurat yang valid (contoh: +62 812 3456 7890)."
            )
        return kontak

    def clean_pengalaman_relevan(self):
        return (self.cleaned_data.get("pengalaman_relevan") or "").strip()

    def clean_kebutuhan_khusus(self):
        return (self.cleaned_data.get("kebutuhan_khusus") or "").strip()


class PendaftaranCreateForm(_ValidasiInformasiPendaftaranMixin, forms.ModelForm):
    """Form pendaftaran relawan baru (atau pengaktifan ulang jika sebelumnya CANCELLED)."""

    class Meta:
        model = PendaftaranRelawan
        fields = [
            "motivasi",
            "kontak_darurat",
            "pengalaman_relevan",
            "kebutuhan_khusus",
        ]

    def __init__(self, *args, relawan=None, kegiatan=None, **kwargs):
        self.relawan = relawan
        self.kegiatan = kegiatan
        self._pendaftaran_lama = None

        if relawan is not None and kegiatan is not None and "instance" not in kwargs:
            self._pendaftaran_lama = PendaftaranRelawan.objects.filter(
                relawan=relawan,
                kegiatan=kegiatan,
            ).first()
            if (
                self._pendaftaran_lama is not None
                and self._pendaftaran_lama.status == StatusPendaftaran.CANCELLED
            ):
                kwargs["instance"] = self._pendaftaran_lama

        super().__init__(*args, **kwargs)
        self.fields["pengalaman_relevan"].required = False
        self.fields["kebutuhan_khusus"].required = False

        if self.relawan is not None:
            self.instance.relawan = self.relawan
        if self.kegiatan is not None:
            self.instance.kegiatan = self.kegiatan

    def clean(self):
        cleaned_data = super().clean()

        if self.relawan is None or self.kegiatan is None:
            raise ValidationError("Data relawan dan kegiatan wajib disertakan.")

        if self._pendaftaran_lama is None:
            self._pendaftaran_lama = PendaftaranRelawan.objects.filter(
                relawan=self.relawan,
                kegiatan=self.kegiatan,
            ).first()

        # Periksa:
        # a. Duplikasi pendaftaran pada kegiatan yang sama
        # b. Kegiatan masih aktif dan jadwal belum lewat
        # c. Kuota kegiatan masih tersedia (sisa_kuota > 0)
        alasan = alasan_tidak_bisa_mendaftar(
            self.relawan,
            self.kegiatan,
            pendaftaran_lama=self._pendaftaran_lama,
        )
        if alasan:
            raise ValidationError(alasan)

        if (
            self._pendaftaran_lama is not None
            and self._pendaftaran_lama.status == StatusPendaftaran.CANCELLED
        ):
            self.instance = self._pendaftaran_lama
            self.instance.siapkan_daftar_ulang()
            for field_name in self.Meta.fields:
                if field_name in cleaned_data:
                    setattr(self.instance, field_name, cleaned_data[field_name])

        return cleaned_data

    def _post_clean(self):
        # Jika ada error non-field (mis. sudah terdaftar), jangan timpa dengan
        # error model.clean() kedua yang pesannya serupa.
        if self.non_field_errors():
            return
        super()._post_clean()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.relawan = self.relawan
        instance.kegiatan = self.kegiatan
        instance.status = StatusPendaftaran.PENDING
        if commit:
            instance.save()
        return instance


class PendaftaranUpdateForm(_ValidasiInformasiPendaftaranMixin, forms.ModelForm):
    """Form pengubahan informasi pendaftaran oleh relawan."""

    class Meta:
        model = PendaftaranRelawan
        fields = [
            "motivasi",
            "kontak_darurat",
            "pengalaman_relevan",
            "kebutuhan_khusus",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["pengalaman_relevan"].required = False
        self.fields["kebutuhan_khusus"].required = False


class PembatalanPendaftaranForm(forms.Form):
    """Form pembatalan pendaftaran relawan beserta alasan pembatalan."""

    alasan_pembatalan = forms.CharField(
        required=True,
        widget=forms.Textarea,
        error_messages={"required": "Alasan pembatalan wajib diisi."},
    )

    def clean_alasan_pembatalan(self):
        alasan = (self.cleaned_data.get("alasan_pembatalan") or "").strip()
        if not alasan:
            raise ValidationError("Alasan pembatalan wajib diisi.")
        if len(alasan) < 5:
            raise ValidationError("Alasan pembatalan minimal terdiri dari 5 karakter.")
        return alasan


class RefleksiRiwayatForm(forms.ModelForm):
    """Form pengisian refleksi/kesan relawan pada riwayat partisipasi."""

    class Meta:
        model = PendaftaranRelawan
        fields = ["refleksi_relawan"]

    def clean_refleksi_relawan(self):
        refleksi = (self.cleaned_data.get("refleksi_relawan") or "").strip()
        if not refleksi:
            raise ValidationError("Refleksi partisipasi wajib diisi.")
        if len(refleksi) < 5:
            raise ValidationError("Refleksi partisipasi minimal terdiri dari 5 karakter.")
        return refleksi
# =====================================================================
# === END BAGIAN MICGUEL (MODUL 3: ALUR RELAWAN / PENDAFTARAN) ========
# =====================================================================

