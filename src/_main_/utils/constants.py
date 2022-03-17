"""
This file contains Global constants used throughout the codebase.
"""

from _main_.settings import IS_PROD, IS_CANARY, BASE_DIR
from _main_.utils.utils import load_json


GLOBAL_SITE_SETTINGS = {"ADMIN_SITE_HEADER": "MassEnergize SuperAdmin Portal"}

CREATE_ERROR_MSG = "An error occurred during creation."

READ_ERROR_MSG = "An error occurred while fetching the requested resource(s)"

COMMUNITY_URL_ROOT = (
    "https://community.massenergize.org"
    if IS_PROD
    else "https://community-canary.massenergize.org"
    if IS_CANARY
    else "https://community.massenergize.dev"
)

ADMIN_URL_ROOT = (
    "https://admin.massenergize.org"
    if IS_PROD
    else "https://admin-canary.massenergize.org"
    if IS_CANARY
    else "https://admin.massenergize.dev"
)

# TODO: @Add more words to this reserved list
RESERVED_SUBDOMAIN_LIST = load_json(
    BASE_DIR + "/_main_/utils/json_files/reserved_subdomains.json"
)

STATES = load_json(BASE_DIR + "/database/raw_data/other/states.json")