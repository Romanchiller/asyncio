import aiohttp
import asyncio
from more_itertools import chunked
from models import init_db, close_db, SwapiPeople, Session

CHUNK_SIZE = 10


async def get_person(person_id: int, session):

    response = await session.get(f'https://swapi.dev/api/people/{person_id}/')
    json_response = await response.json()

    return json_response


async def get_pole(session, obj, name):

    response = await session.get(obj)
    obj_json = await response.json()

    return obj_json[name]


async def handle(session, info: dict, key: str, name: str):
    if isinstance(info[key], str):
        response = await session.get(info[key])
        response_json = await response.json()
        info[key] = response_json[name]
        return info

    if len(info[key]) > 0:
        objs_title = [get_pole(session, obj, name) for obj in info[key]]
        result = await asyncio.gather(*objs_title)
        objs_str = ','.join(result)
        info[key] = objs_str
    else:
        info[key] = ''
    return info


async def form_person(person_id: int, session):

    info = await get_person(person_id, session)

    try:
        await handle(session, info, 'homeworld', 'name')
        await handle(session, info, 'films', 'title')
        await handle(session, info, 'vehicles', 'name')
        await handle(session, info, 'species', 'name')
        await handle(session, info, 'starships', 'name')
        del info['created']
        del info['edited']
        del info['url']
    except KeyError:
        return info
    return info


async def insert_people(people_list):
    people_list = [SwapiPeople(name=person['name'],
                               height=person['height'],
                               mass=person['mass'],
                               hair_color=person['hair_color'],
                               skin_color=person['skin_color'],
                               eye_color=person['eye_color'],
                               birth_year=person['birth_year'],
                               gender=person['gender'],
                               homeworld=person['homeworld'],
                               films=person['films'],
                               species=person['species'],
                               starships=person['starships'],
                               vehicles=person['vehicles'],) for person in people_list if 'detail' not in person]

    async with Session() as session:
        session.add_all(people_list)
        await session.commit()


async def main():

    await init_db()
    session = aiohttp.ClientSession()
    async with session as session:
        for people_id_chunk in chunked(range(1, 90), CHUNK_SIZE):
            coros = [form_person(people_id, session) for people_id in people_id_chunk]
            result = await asyncio.gather(*coros)
            print(result)
            task = asyncio.create_task(insert_people(result))
            print(task)
        tasks = asyncio.all_tasks() - {asyncio.current_task()}
        print(tasks)
        await asyncio.gather(*tasks)
    await close_db()


if __name__ == '__main__':
    asyncio.run(main())
