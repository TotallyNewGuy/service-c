import pytz
from datetime import datetime
from quart import Blueprint, request

from query_service import get_or_cache


timezone = pytz.timezone("America/Chicago")

# create a blueprint for url prefix
query_blueprint = Blueprint('query_api', __name__, url_prefix='/query')

@query_blueprint.route('/')
async def most_recent_trips():
    prev = request.args.get('prev', default = 10, type = int)
    future = request.args.get('future', default = 5, type = int)

    current_time = datetime.now(timezone)
    midnight = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    time_diff = current_time - midnight
    curr_time = int(time_diff.total_seconds())

    res = await get_or_cache(curr_time=curr_time, prev=prev, future=future)
    return res, 200