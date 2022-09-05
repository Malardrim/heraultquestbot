from decouple import config
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(config('BDD_URI'))
db = client[config('BDD_NAME')]

async def do_insert(document, collection: str):
    await db[collection].insert_one(document)

async def do_find_one(filters, collection: str):
    document = await db[collection].find_one(filters)
    return document

async def do_replace(document, collection: str):
    _id = document['_id']
    coll = db[collection]
    await coll.replace_one({'_id': _id}, document)
    return await coll.find_one({'_id': _id})