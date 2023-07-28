from api.utils.api_utils import get_postmark_template
ME_SUPPORT_TEAM_EMAIL = "support@massenergize.org"
# API user types  

# if (IS_PROD):
#   DATA_DOWNLOAD_TEMPLATE_ID = "28578196"
#   SADMIN_EMAIL_TEMPLATE_ID = "28578198"
#   CADMIN_EMAIL_TEMPLATE_ID = "28578195"
#   USER_WELCOME_EMAIL_TEMPLATE_ID = "28578199"
#   GUEST_USER_EMAIL_TEMPLATE_ID = "28578197"
#   WEEKLY_EVENTS_NUDGE_TEMPLATE_ID="30038176"
#   YEARLY_MOU_TEMPLATE_ID = "31025296" # Change to PROD template when template is finalised before deployment
#   MOU_SIGNED_ADMIN_RECEIPIENT = "31128813"
#   MOU_SIGNED_SUPPORT_TEAM_TEMPLATE = "31138501"
#   USER_EVENTS_NUDGE_TEMPLATE_ID = "30986598"
# elif (IS_LOCAL):
#   # using Testing Server templates, except those with attachments which use Development server
#   DATA_DOWNLOAD_TEMPLATE_ID = "27864141" # Dev server
#   SADMIN_EMAIL_TEMPLATE_ID = "28790439"
#   CADMIN_EMAIL_TEMPLATE_ID = "28790435"
#   USER_WELCOME_EMAIL_TEMPLATE_ID = "28790440"
#   GUEST_USER_EMAIL_TEMPLATE_ID = "28437705"
#   WEEKLY_EVENTS_NUDGE_TEMPLATE_ID="30038358"
#   YEARLY_MOU_TEMPLATE_ID = "31025296"
#   MOU_SIGNED_ADMIN_RECEIPIENT = "31128813"
#   MOU_SIGNED_SUPPORT_TEAM_TEMPLATE = "31138501" # Dev server
#   USER_EVENTS_NUDGE_TEMPLATE_ID="31629138"
# else:
#   DATA_DOWNLOAD_TEMPLATE_ID = "27864141"
#   SADMIN_EMAIL_TEMPLATE_ID = "27843576"
#   CADMIN_EMAIL_TEMPLATE_ID = "27853283"
#   USER_WELCOME_EMAIL_TEMPLATE_ID = "27142713"
#   GUEST_USER_EMAIL_TEMPLATE_ID = "28437705"
#   WEEKLY_EVENTS_NUDGE_TEMPLATE_ID="29520140"
#   YEARLY_MOU_TEMPLATE_ID = "31025307"
#   MOU_SIGNED_ADMIN_RECEIPIENT = "31128813"
#   MOU_SIGNED_SUPPORT_TEAM_TEMPLATE = "31138501"
#   USER_EVENTS_NUDGE_TEMPLATE_ID="30986598"

CADMIN_EMAIL = "Cadmin Email"
DATA_DOWNLOAD = "Data Download"
GUEST_USER_EMAIL = "Guest User Email"
MOU_SIGNED_ADMIN_RECIPIENT = "Mou Signed Admin Recipient"
MOU_SIGNED_SUPPORT_TEAM = "Mou Signed Support Team"
SADMIN_EMAIL = "Sadmin Email"
USER_WELCOME_EMAIL = "User Welcome Email"
USER_EVENTS_NUDGE="User Events Nudge"
WEEKLY_EVENTS_NUDGE="Weekly Events Nudge"
YEARLY_MOU = "Yearly MOU"
USER_EMAIL_VERIFICATION="User Email Verification"
