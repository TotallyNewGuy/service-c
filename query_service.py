
import json
from sqlalchemy import and_
from collections import defaultdict

from db_util import get_db
from models import CsvData
from sqlalchemy.future import select
from redis_util import get_redis_client

redis_key_retention_time = 60


async def get_or_cache(**kwargs):
    sorted_keys = sorted(kwargs.keys())
    cache_key = "_".join([f"{key}{kwargs[key]}" for key in sorted_keys if key != "curr_time"])
    cache_res = await get_redis_client().get(cache_key)
    # if there is no cache, query the result and save it into Redis
    if cache_res is None:
        async for db_session in get_db():
            query_res = await get_recent_trips(db_session, **kwargs)
            list_res = [obj.as_dict() for obj in query_res]
            grouped_dict = defaultdict(list)
            for item in list_res:
                timepointid = item["timepointid"]
                grouped_dict[timepointid].append(item)
            grouped_dict = dict(grouped_dict)

            json_str = json.dumps(grouped_dict)
            await get_redis_client().set(cache_key, json_str, ex=redis_key_retention_time)
            print("from Postgresql")
            grouped_dict["from"] = "Postgresql"
            return grouped_dict
    else:
        print("from Redis")
        json_obj = json.loads(cache_res)
        json_obj["from"] = "Redis"
        return json_obj


async def get_recent_trips(session, curr_time, prev, future):
    prev_sec = prev * 60
    future_sec = future * 60
    query = select(CsvData).filter(
        and_(CsvData.schd_time >= curr_time - prev_sec,
             CsvData.schd_time < curr_time + future_sec
        )
    )
    result = await session.execute(query)
    results = result.scalars().all()
    return results