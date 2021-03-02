from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.config import (
    FILING_FORM_NAMES_VERSIONS
)
from app.schemas.lobbyist.new_lobbyist_filing import (
    NewLobbyistFiling
)
from app.models.crud.lobbyist import (
    get_lobbying_entity_current_contact_info_by_id,
    get_registered_lobbyists,
    get_registered_clients,
    get_registered_muni_decisions_firm
)
from app.models.crud.filings import (
    get_raw_filing_by_id,
    get_latest_filing_by_entity_id_and_filing_type_and_year
)
from app.models.entities import (
    LobbyingEntity,
)
from app.models.filings import (
    Filing
)

async def populate_lobbyist_amendment_form(
    db_session: Session,
    payload: NewLobbyistFiling,
    filing: Filing
):

    raw = await get_raw_filing_by_id(db_session, filing.amends_prev_id)
    form = dict(raw.raw_json)

    form['filing_id'] = filing.filing_id
    form['amendment'] = filing.amendment
    form['amends_id'] = filing.amends_prev_id

    contact_info = await get_lobbying_entity_current_contact_info_by_id(
        db_session,
        filing.entity_id
    )
    if contact_info is None:
        raise Http400(detail="Lobbying entity is missing contact info.")

    form['filer'] = {}

    if 'fees' in form.keys():
        del form['fees']

    # reset verification
    form['verification'] = {
        "filer_id": None,
        "filer_title": None,
        "location": None,
        "date": None,
        "signature": None
    }
    
    
    finfo = form['lobbying_entity_contact_info']
    cinfo = jsonable_encoder(contact_info)
    for key in finfo.keys():
        finfo[key] = cinfo[key]
    
    return form

async def populate_core_new_lobbyist_form(
    db_session: Session,
    payload: NewLobbyistFiling,
    filing_type: str,
    form: dict,
    entity: LobbyingEntity,
    filing: Filing
) -> dict:

    form['filing_id'] = filing.filing_id
    form['year'] = payload.year
    form['amendment'] = False
    form['meta']['form_name'] = FILING_FORM_NAMES_VERSIONS[filing_type]

    if filing_type in ['ec601','ec602']:
        contact_info = await get_lobbying_entity_current_contact_info_by_id(
            db_session,
            entity.entity_id
        )
        if contact_info is None:
            raise Http400(detail="Lobbying entity is missing contact info.")

        finfo = form['lobbying_entity_contact_info']
        cinfo = jsonable_encoder(contact_info)
        for key in finfo.keys():
            finfo[key] = cinfo[key]
    elif filing_type in ['ec603']:
        form['quarter'] = payload.quarter
        form['period_start'] = str(filing.period_start)
        form['period_end'] = str(filing.period_end)
            
    return form

# 8c7b7c36-26b0-eb5c-eb26-7ecdf0480be5

def map_entity(obj):
    org = not obj.individual
    xd = {
        "id": obj.entity_id,
        "individual": obj.individual,
        "org_name": obj.name_last_or_org if org else None,
        "first_name": obj.name_first if not org else None,
        "middle_name": obj.name_middle if not org else None,
        "last_name": obj.name_last_or_org if not org else None,
        "address": {
            "address1": obj.address1,
            "address2": obj.address2,
            "city": obj.city,
            "zipcode": obj.zipcode,
            "state": obj.state,
            "phone": obj.phone
        }
    }
    return xd
    

async def get_registered_data(
    db_session: Session,
    filing: Filing,
    form: dict
):

    if filing.filing_type == 'ec603':
        filing_type = 'ec601'
    elif filing.filing_type == 'ec604':
        filing_type = 'ec602'
    else:
        raise Http400(detail="Incorrect filing type.")
    
    year = form['year']
    entity_id = filing.entity_id

    # get most recent registration
    registration = await get_latest_filing_by_entity_id_and_filing_type_and_year(
        db_session,
        entity_id,
        filing_type,
        year
    )

    lobbyists = await get_registered_lobbyists(db_session, registration)

    lobbyist_list = []
    for ll in lobbyists:
        xd = map_entity(ll)
        lobbyist_list.append(xd)

    if filing.filing_type == 'ec603':
        clients = await get_registered_clients(db_session, registration)
        client_list = []
        for ll in clients:
            xd = map_entity(ll[1])
            xd['client_description'] = ll[0].client_description
            client_list.append(xd)
    else:
        clients = []

    muni_decisions = await get_registered_muni_decisions_firm(db_session, registration)

    muni_decision_list = []
    for md in muni_decisions:
        xd = {
            "id": md[0].decision_id,
            "client_id": md[1].lobby_entity_id,
            "description_short": md[0].description_short,
            "description_detail": md[0].description_detail,
            "outcome_sought": md[0].outcome_sought
        }
        muni_decision_list.append(xd)

    xd = { "lobbyists": lobbyist_list,
           "clients": client_list,
           "muni_decisions": muni_decision_list
       }
    return xd

async def populate_quarterly_registered_data(
    db_session: Session,
    filing_type: str,
    form: dict,
    filing: Filing
):

    registered = await get_registered_data(db_session, filing, form)

    form['registered'] = registered
    
    return form
    

    


def compute_ec601_fees(kind, schedule, raw_filing, config):
    xd = {}
    # sort
    raw_filing["directory"]["entity"].sort(key=lambda x: x['effective_date'])
    for entity in raw_filing[schedule]:
        eff_date = [x["effective_date"] for x in raw_filing["directory"]["entity"]
                    if x["id"] == entity[f"{kind}_entity_id"]][0]
        sched = [x for x in config['fee_schedule']
                 if x["start"] <= eff_date and x["end"] >= eff_date][0]
        date_range = f"{sched['start'].strftime('%m/%d/%Y')} "\
                     f"- {sched['end'].strftime('%m/%d/%Y')}"
        if date_range not in xd.keys():
            xd[date_range] = { "fee": sched[kind], "count": 1}
        else:
            xd[date_range]['count'] += 1

    # now re-arrange for convenience
    xlist = []
    for key in xd:
        new_dict = {
            "effective_date_in": key,
            "fee": xd[key]['fee'],
            "count": xd[key]['count']
        }
        xlist.append(new_dict)

    return xlist
                
def simplify_fees(fees: dict, filing: Filing):

    if filing.filing_type == 'ec601':

        lobbyist_count = 0
        lobbyist_fees = 0.0

        for lobb in fees['lobbyists']['details']:
            lobbyist_count += lobb['count']
            lobbyist_fees += lobb['fee']*lobb['count']

        client_count = 0
        client_fees = 0
        
        for lobb in fees['clients']['details']:
            client_count += lobb['count']
            client_fees += lobb['fee']*lobb['count']

        res = {
            "lobbyists": lobbyist_count,
            "lobbyist_fees": lobbyist_fees,
            "clients": client_count,
            "client_fees": client_fees
        }

        return res

    else:
        Http400(details="ec602 not yet implemented here.")
