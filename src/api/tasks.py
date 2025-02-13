import csv
from django.http import HttpResponse
from _main_.utils.context import Context
from _main_.utils.emailer.send_email import send_massenergize_email, send_massenergize_email_with_attachments
from api.constants import ACTION_USERS, ACTIONS, COMMUNITIES, METRICS, SAMPLE_USER_REPORT, TEAMS, USERS, CADMIN_REPORT, SADMIN_REPORT
from api.store.download import DownloadStore
from api.constants import DOWNLOAD_POLICY
from api.store.common import create_pdf_from_rich_text, sign_mou
from api.store.utils import get_user_from_context
from api.utils.api_utils import get_postmark_template
from database.models import Policy
from task_queue.events_nudge.cadmin_events_nudge import generate_event_list_for_community, send_events_report
from api.store.utils import get_community, get_user
from celery import shared_task
from api.store.download import DownloadStore
from api.utils.constants import CADMIN_EMAIL, DATA_DOWNLOAD, SADMIN_EMAIL
from database.models import Community, CommunityAdminGroup, CommunityMember, UserActionRel, UserProfile
from django.utils import timezone
import datetime
from django.utils.timezone import utc
from django.db.models import Count

from task_queue.events_nudge.user_event_nudge import prepare_user_events_nudge


def generate_csv_and_email(data, download_type, community_name=None, email=None):
    response = HttpResponse(content_type="text/csv")
    if not community_name:
        filename = "all-%s-data.csv" % download_type
    else:
        filename = "%s-%s-data.csv" % (community_name, download_type)
    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)
    user = UserProfile.objects.get(email=email)
    temp_data = {
        'data_type': download_type,
        "name":user.full_name,
    }
    send_massenergize_email_with_attachments(get_postmark_template(DATA_DOWNLOAD),temp_data,[email], response.content, filename)
    return True


def error_notification(download_type, email):
    msg = f'Sorry, an error occurred while generating {download_type} data. Please try again.'
    send_massenergize_email(f"{download_type.capitalize()} Data",msg, email )


@shared_task(bind=True)
def download_data(self, args, download_type):
    store = DownloadStore()
    context = Context()
    context.user_is_community_admin = args.get("user_is_community_admin", False)
    context.user_is_super_admin = args.get("user_is_super_admin", False)
    context.user_is_logged_in = args.get("user_is_logged_in", False)
    context.user_email = args.get("email", None)
    email = args.get("email", None)
    if download_type == USERS:
        (files, com_name), err = store.users_download(context, community_id=args.get("community_id"), team_id=args.get("team_id"))
        if  err:
            error_notification(USERS, email)
        else:
            generate_csv_and_email(data=files, download_type=USERS, community_name=com_name, email=email)

    elif download_type == ACTIONS:
        (files, com_name), err = store.actions_download(context, community_id=args.get("community_id"))
        if err:
            error_notification(ACTIONS, email)
        else:
            generate_csv_and_email(data=files, download_type=ACTIONS, community_name=com_name, email=email)
    

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
            generate_csv_and_email(data=files, download_type=TEAMS, community_name=com_name, email=email)

    elif download_type == METRICS:
        (files, com_name), err = store.metrics_download(context, args, community_id=args.get("community_id"))
        if err:
            error_notification(METRICS, email)
        else:
            generate_csv_and_email(
                data=files, download_type=METRICS, community_name=com_name, email=email)

    elif download_type == CADMIN_REPORT:
        user, err = get_user(None, email)
        community_id = args.get("community_id", None)
        community_list = []
        if community_id:
             com, err = get_community(community_id)
             community_list[0] = com
        else:
            admin_groups = user.communityadmingroup_set.all()
            for grp in admin_groups:
                com = grp.community
                community_list.append(com)

        for com in community_list:
            events = generate_event_list_for_community(com)
            event_list = events.get("events", [])
            stat = send_events_report(user.full_name, user.email, event_list)        
            if not stat:
                error_notification(CADMIN_REPORT, email)
                return
            
    elif download_type == SAMPLE_USER_REPORT:
        prepare_user_events_nudge(email=email, community_id=args.get("community_id"))

    elif download_type == ACTION_USERS:
       (files, action_name), err = store.action_users(context,action_id=args.get("action_id"))
       if err:
           error_notification(ACTION_USERS, email)
       else:
           generate_csv_and_email(data=files, download_type=ACTION_USERS, community_name=action_name, email=email)

    elif download_type == DOWNLOAD_POLICY:
        policy = Policy.objects.filter(id=args.get("policy_id")).first()
        rich_text = sign_mou(policy.description)
        pdf,_ = create_pdf_from_rich_text(rich_text,args.get("title"))
        user = get_user_from_context(context)
        temp_data = {
        'data_type': "Policy Document",
        "name":user.full_name,
    }
        send_massenergize_email_with_attachments(get_postmark_template(DATA_DOWNLOAD),temp_data,[user.email], pdf,f'{args.get("title")}.pdf')


@shared_task(bind=True)
def generate_and_send_weekly_report(self):
    today = datetime.datetime.utcnow().replace(tzinfo=utc)
    one_week_ago = today - timezone.timedelta(days=7)
    super_admins = UserProfile.objects.filter(is_super_admin=True, is_deleted=False).values_list("email", flat=True)

    communities = Community.objects.all().order_by('is_approved')
    communities_total_signups = CommunityMember.objects.filter(community__is_approved=True).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_weekly_signups = CommunityMember.objects.filter(community__is_approved=True, created_at__gte=one_week_ago).values('community__name').annotate(signups=Count("community")).order_by('community')
    communities_total_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago).exclude(status='SAVE_FOR_LATER').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_done_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status='DONE').values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')
    communities_weekly_todo_actions = UserActionRel.objects.filter(created_at__gte=one_week_ago, created_at__lte=today, status="TODO").values('action__community__name', 'carbon_impact').annotate(actions=Count("action__community")).order_by('action__community')

    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    writer.writerow(['Community','Total Signups', 'Signups This Week', 'Total Actions Taken', ' Actions Taken This Week ', 'Actions in ToDo This Week'])

    for community in communities:
        community_name = community.name
        all_community_admins = CommunityAdminGroup.objects.filter(community=community).values_list('members__email', flat=True)
        all_community_admins = list(all_community_admins)



        total_signups  = communities_total_signups.filter(community__name=community_name).first()
        community_total_signup = total_signups['signups'] if total_signups else 0
        weekly_signups = communities_weekly_signups.filter(community__name=community_name).first()
        community_weekly_signup = weekly_signups['signups'] if weekly_signups else 0

        total_actions = communities_total_actions.filter(action__community__name=community_name).first()
        community_actions_taken = total_actions['actions'] if total_actions else 0

        weekly_done_actions = communities_weekly_done_actions.filter(action__community__name=community_name).first()
        community_weekly_done_actions = weekly_done_actions['actions'] if weekly_done_actions else 0

        weekly_todo_actions = communities_weekly_todo_actions.filter(action__community__name=community_name).first()
        community_weekly_todo_actions = weekly_todo_actions['actions'] if weekly_todo_actions else 0


        cadmin_temp_data ={
            'community': community_name,
            'signups': community_weekly_signup,
            'actions_done': community_weekly_done_actions,
            'actions_todo': community_weekly_todo_actions,
            'start': str(one_week_ago.date()),
            'end': str(today.date()),

        }
        

        send_email(None, None,all_community_admins, get_postmark_template(CADMIN_EMAIL),cadmin_temp_data)

        writer.writerow([community_name, community_total_signup,community_weekly_signup, community_actions_taken, community_weekly_done_actions, community_weekly_todo_actions])
    
    sadmin_temp_data =  {
            'name':"there",
            'start': str(one_week_ago.date()),
            'end': str(today.date()),
        }

    send_email(response.content, f'Weekly Report({one_week_ago.date()} to {today.date()}).csv',list(super_admins), get_postmark_template(SADMIN_EMAIL), sadmin_temp_data )
    return "success"



def send_email(file, file_name, email_list, temp_id, t_model):
    send_massenergize_email_with_attachments(temp_id, t_model, email_list, file, file_name)



@shared_task(bind=True)
def deactivate_user(self,email):
    user = UserProfile.objects.filter(email=email).first()
    if user:
        user.delete()