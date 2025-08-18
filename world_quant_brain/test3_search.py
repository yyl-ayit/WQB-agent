
from datetime import datetime
from os.path import expanduser

from wqb import FilterRange
from wqb import WQBSession, print


with open(expanduser('./brain_credentials_copy')) as f:
    credentials = eval(f.read())
username, password = credentials
# Create `wqbs`
wqbs = WQBSession((username, password))

lo = datetime.fromisoformat('2025-06-20T00:00:00-05:00')
hi = datetime.fromisoformat('2025-08-15T00:00:00-05:00')
resps = wqbs.filter_alphas(
    status='UNSUBMITTED',
    region='USA',
    delay=1,
    universe='TOP3000',
    sharpe=FilterRange.from_str('[1.0, inf)'),
    fitness=FilterRange.from_str('[0.7, inf)'),
    turnover=FilterRange.from_str('(-inf, 0.7]'),
    date_created=FilterRange.from_str(f"[{lo.isoformat()}, {hi.isoformat()})"),
    order='dateCreated',
)
alpha_ids = []
alpha = {
    "type": "REGULAR",
    "regular": ''
}
alphas = []
for resp in resps:
    # for i in resp.json()['results']:
        # alpha['settings'] = i['settings']
        # alpha['regular'] = i['regular']['code']
        # alphas.append(alpha)
        # resp = asyncio.run(
        #     wqbs.simulate(
        #         alpha,  # `alpha` or `multi_alpha`
        #         on_nolocation=lambda vars: print(vars['target'], vars['resp'], sep='\n'),
        #         on_start=lambda vars: print(vars['url']),
        #         on_finish=lambda vars: print(vars['resp']),
        #         on_success=lambda vars: print(vars['resp']),
        #         on_failure=lambda vars: print(vars['resp']),
        #     )
        # )
        # print(resp.status_code)
        # print(resp.text)
    alpha_ids.extend(item['regular']['code'] for item in resp.json()['results'])
print(len(alpha_ids))
print(alpha_ids)

