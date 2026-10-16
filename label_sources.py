"""Shared official-label source resolution for both MediLens workspaces."""
import urllib.parse
FALLBACK='https://dailymed.nlm.nih.gov/dailymed/webservices-help/v2/spls_api.cfm'
def daily_med_url(label,openfda):
    value=openfda.get('spl_set_id')
    set_id=str(value[0]) if isinstance(value,list) and value else str(value or label.get('set_id') or '')
    return 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid='+urllib.parse.quote(set_id) if set_id else FALLBACK
