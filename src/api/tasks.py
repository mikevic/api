import csv
from django.http import HttpResponse
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from api.constants import ACTIONS, COMMUNITIES, METRICS, TEAMS, USERS
from api.store.download import DownloadStore
from celery import shared_task
from api.store.download import DownloadStore
from api.utils.constants import ME_DATA_DOWNLOAD_TEMP_ID
from database.models import UserProfile
import datetime


def generate_csv_and_email(data, download_type, community_name=None, email=None):
    response = HttpResponse(content_type="text/csv")
    now = datetime.datetime.now().strftime("%Y%m%d")
    if not community_name:
        filename = "all-%s-data-%s.csv" % (download_type, now)
    else:
        filename = "%s-%s-data-%s.csv" % (community_name, download_type, now)
    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)
    user = UserProfile.objects.get(email=email)
    temp_data = {
        'data_type': download_type,
        "name":user.full_name,
    }
    
    send_massenergize_email_with_attachments(ME_DATA_DOWNLOAD_TEMP_ID,temp_data,email, response.content, filename)
    return True




def error_notification(download_type, email):
    msg = f'Sorry an error occurred while generating {download_type} data. Please try again.'
    send_massenergize_email(f"{download_type.capitalize()} Data",msg, email )


@shared_task(bind=True)
def download_data(self, args, download_type):
    store = DownloadStore()
    context = Context()
    context.user_is_community_admin = args.get("user_is_community_admin", False)
    context.user_is_super_admin = args.get("user_is_super_admin", False)
    context.user_is_logged_in = args.get("user_is_logged_in", False)

    email = args.get("email", None)

    if download_type == USERS:
        (files, com_name), err = store.users_download(context, community_id=args.get("community_id"), team_id=args.get("team_id"))
        if err:
            error_notification(USERS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=USERS, community_name=com_name, email=email)

    elif download_type == ACTIONS:
        (files, com_name), err = store.actions_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(ACTIONS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=ACTIONS, community_name=com_name, email=email)

    elif download_type == COMMUNITIES:
        (files, dummy), err = store.communities_download(context)
        if err:
            error_notification(COMMUNITIES, email)
        else:   
            generate_csv_and_email(
                data=files, download_type=COMMUNITIES, email=email)

    elif download_type == TEAMS:
        (files, com_name), err = store.teams_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(TEAMS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=TEAMS, community_name=com_name, email=email)

    elif download_type == METRICS:
        (files, com_name), err = store.metrics_download(context, args, community_id=args.get("community_id"))
        if err:
            error_notification(METRICS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=METRICS, community_name=com_name, email=email)
