from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone

from bookings.models import Reminder


class Command(BaseCommand):
    help = "Рассылка напоминаний по броням"

    def handle(self, *args, **options):
        now = timezone.now()

        reminders = (
            Reminder.objects.select_related("booking", "booking__user")
            .filter(
                is_sent=False,
                scheduled_for__lte=now,
            )
        )

        if not reminders.exists():
            self.stdout.write(self.style.SUCCESS("Нет напоминаний для отправки."))
            return

        for reminder in reminders:
            booking = reminder.booking
            user = booking.user

            subject = "Напоминание о бронировании"

            message = (
                f"Здравствуйте, {user.username}!\n\n"
                f"Напоминаем, что у вас забронировано место {booking.parking_spot.number} "
                f"на {booking.date:%d.%m.%Y} "
                f"с {booking.start_time:%H:%M} "
                f"до {booking.end_time:%H:%M}.\n"
                "Если планы изменились, отмените бронь."
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                reminder.is_sent = True
                reminder.sent_at = timezone.now()
                reminder.save(update_fields=["is_sent", "sent_at"])

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Напоминание отправлено пользователю {user.email} (бронь №{booking.pk})."
                    )
                )

            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Ошибка отправки напоминания для брони №{booking.pk}: {exc}"
                    )
                )
