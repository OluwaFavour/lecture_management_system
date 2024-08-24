from django.core.mail import send_mail
from django.conf import settings as django_settings

from .models import Alert, AlertSettings
from lecture_management_system.utils import log


def send_alerts():
    """
    Send alerts to all users who have active alerts

    Returns:
    list[Exception]: A list of errors that occurred while sending alerts
    """
    # Get all users with active alerts
    errors: list[Exception] = []

    # Get alerts that should be sent and where students opted for email notifications
    alerts = Alert.objects.filter(
        should_alert=True, students__alert_settings__via_email=True
    ).distinct()

    # Map descriptions to recipient emails
    mail_title_to_description_to_recipients_email_map: dict[
        str, dict[str, set[str]]
    ] = {}

    for alert in alerts:
        if alert.title not in mail_title_to_description_to_recipients_email_map:
            mail_title_to_description_to_recipients_email_map[alert.title] = {}
        if (
            alert.description
            not in mail_title_to_description_to_recipients_email_map[alert.title]
        ):
            mail_title_to_description_to_recipients_email_map[alert.title][
                alert.description
            ] = set()
        mail_title_to_description_to_recipients_email_map[alert.title][
            alert.description
        ].update(
            alert.students.filter(alert_settings__via_email=True).values_list(
                "email", flat=True
            )
        )

    for (
        title,
        description_to_recipients_email_map,
    ) in mail_title_to_description_to_recipients_email_map.items():
        for description, recipients in description_to_recipients_email_map.items():
            try:
                send_mail(
                    title=f"Alert from Lecture Management System: {title}",
                    message=description,
                    from_email=django_settings.FROM_EMAIL,
                    recipient_list=recipients,
                    fail_silently=False,
                )
                log.info(f"Sent alert to {recipients}")
            except Exception as e:
                errors.append(e)

    return errors
    # description_to_recipients_email_map: dict[str, set[str]] = {}

    # for alert in alerts:
    #     if alert.description not in description_to_recipients_email_map:
    #         description_to_recipients_email_map[alert.description] = set()
    #     description_to_recipients_email_map[alert.description].update(
    #         alert.students.filter(alert_settings__via_email=True).values_list(
    #             "email", flat=True
    #         )
    #     )

    # # Send the alerts to the recipients
    # for description, recipients in description_to_recipients_email_map.items():
    #     try:
    #         send_mail(
    #             title="Alert from Lecture Management System",
    #             message=description,
    #             from_email=django_settings.FROM_EMAIL,
    #             recipient_list=recipients,
    #             fail_silently=False,
    #         )
    #         log.info(f"Sent alert to {recipients}")
    #         # TODO: Implement sending SMS alerts
    #     except Exception as e:
    #         errors.append(e)


def send_alert_with_mail(alert: Alert):
    user = alert.user
    settings: AlertSettings = user.alert_settings
    if not alert.is_active or not alert.should_alert:
        raise ValueError("Alert is not active or should not be triggered")
    elif not settings.via_email:
        raise ValueError("User has disabled email alerts")
    send_mail(
        title=alert.title,
        message=alert.description,
        from_email=django_settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_alert_with_sms(alert: Alert):
    user = alert.user
    settings: AlertSettings = user.alert_settings
    if not alert.is_active or not alert.should_alert:
        raise ValueError("Alert is not active or should not be triggered")
    elif not settings.via_sms:
        raise ValueError("User has disabled sms alerts")
    # Send SMS alert
    pass
