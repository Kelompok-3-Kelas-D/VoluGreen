"""Load the coursework demo catalogue from a versioned JSON dataset."""

import json
from datetime import datetime, time, timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.models import Category, OrganizationSubmission, Profile
from organizer.models import Kegiatan


DATASET = Path(__file__).resolve().parents[2] / "fixtures" / "initial_activities.json"


class Command(BaseCommand):
    help = "Tambahkan 60 kegiatan simulasi terbit dari JSON, aman dijalankan berulang."

    def handle(self, *args, **options):
        try:
            data = json.loads(DATASET.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Dataset kegiatan tidak dapat dibaca: {exc}") from exc

        organizers = data.get("organizers", [])
        activities = data.get("activities", [])
        organizer_keys = [item.get("key") for item in organizers]
        activity_keys = [item.get("key") for item in activities]
        activity_names = [item.get("nama") for item in activities]
        if len(activities) < 50:
            raise CommandError("Dataset harus memuat minimal 50 kegiatan.")
        if not organizers or len(set(organizer_keys)) != len(organizer_keys):
            raise CommandError("Kode penyelenggara dalam dataset harus unik.")
        if len(set(activity_keys)) != len(activity_keys) or len(set(activity_names)) != len(activity_names):
            raise CommandError("Kode dan nama kegiatan dalam dataset harus unik.")
        if any(item.get("organizer") not in organizer_keys for item in activities):
            raise CommandError("Ada kegiatan dengan penyelenggara yang tidak tercantum dalam dataset.")

        user_model = get_user_model()
        today = timezone.localdate()
        created_count = 0
        renamed_count = 0
        with transaction.atomic():
            users = {}
            for row in organizers:
                username = row["key"]
                email = f"{username}@seed.volugreen.invalid"
                user, created = user_model.objects.get_or_create(
                    username=username, defaults={"email": email}
                )
                # Lock the seed account so simultaneous deployment workers serialize its activities.
                user = user_model.objects.select_for_update().get(pk=user.pk)
                if created:
                    user.set_unusable_password()
                    user.save(update_fields=["password"])
                elif user.email != email or user.has_usable_password():
                    raise CommandError(f"Akun {username} sudah dipakai di luar data simulasi.")
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "role": Profile.Role.ORGANIZER,
                        "phone_number": "0000000000",
                        "city": row["city"],
                        "organization_name": row["name"],
                        "organization_type": row["type"],
                    },
                )
                if profile.role != Profile.Role.ORGANIZER:
                    raise CommandError(f"Profil {username} bukan penyelenggara.")
                OrganizationSubmission.objects.get_or_create(
                    contact_email=email,
                    defaults={
                        "name": row["name"],
                        "type": profile.get_organization_type_display(),
                        "city": row["city"],
                        "description": "Organisasi simulasi untuk demonstrasi VoluGreen.",
                        "status": OrganizationSubmission.Status.VERIFIED,
                        "verified_at": timezone.now(),
                        "verified_by": "initial_data",
                    },
                )
                users[username] = user

            categories = {}
            for row in activities:
                category_name = row["kategori"]
                if category_name not in categories:
                    categories[category_name], _ = Category.objects.get_or_create(name=category_name)
                starts_on = today + timedelta(days=int(row["mulai_dalam_hari"]))
                starts_at = timezone.make_aware(
                    datetime.combine(starts_on, time(hour=int(row["jam_mulai"]))),
                    timezone.get_current_timezone(),
                )
                owner = users[row["organizer"]]
                activity = Kegiatan.objects.filter(organizer=owner, nama=row["nama"]).first()
                if activity is None:
                    old_title = f"[Demo {row['key'].removeprefix('demo-')}] {row['nama']}"
                    activity = Kegiatan.objects.filter(organizer=owner, nama=old_title).first()
                    if activity is not None:
                        activity.nama = row["nama"]
                        activity.save(update_fields=["nama", "diperbarui_pada"])
                        renamed_count += 1
                if activity is None:
                    Kegiatan.objects.create(
                        organizer=owner,
                        nama=row["nama"],
                        deskripsi=row["deskripsi"],
                        kategori=categories[category_name],
                        tanggal_mulai=starts_at,
                        nama_lokasi=row["nama_lokasi"],
                        alamat=row["alamat"],
                        kota=row["kota"],
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        kuota=row["kuota"],
                        status_publikasi=Kegiatan.StatusPublikasi.PUBLISHED,
                    )
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Data awal siap: {len(activities)} kegiatan pada JSON, {created_count} baru, {renamed_count} judul lama diperbarui."
        ))
