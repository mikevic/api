from _main_.utils.massenergize_errors import MassEnergizeAPIError
from _main_.utils.massenergize_response import MassenergizeResponse
from api.store.summary import SummaryStore
from typing import Tuple

class SummaryService:
  """
  Service Layer for all the summaries
  """

  def __init__(self):
    self.store =  SummaryStore()

  def summary_for_community_admin(self, context, community_id) -> Tuple[list, MassEnergizeAPIError]:
    summary, err = self.store.summary_for_community_admin(context, community_id)
    if err:
      return None, err
    return summary, None


  def summary_for_super_admin(self, context) -> Tuple[list, MassEnergizeAPIError]:
    summary, err = self.store.summary_for_super_admin(context)
    if err:
      return None, err
    return summary, None
