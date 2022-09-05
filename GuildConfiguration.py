from pprint import pprint
import db_connection

collection_name = 'guild_configuration'

async def update_guild_configuration(guild_id: str, channel_organisation: str = None, channel_inscription: str = None):
    config = await get_config(guild_id)
    if config is None:
        config = {
            'guild_id': guild_id,
            'channel_organisation': channel_organisation,
            'channel_inscription': channel_inscription,
        }
        await db_connection.do_insert(config, collection_name)
        return await get_config(guild_id, True)
    else:
        if channel_organisation is not None:
            config['channel_organisation'] = channel_organisation
        if channel_inscription is not None:
            config['channel_inscription'] = channel_inscription
        return await get_config(guild_id, True)

async def get_config(guild_id: str, force: bool = False):
    return await db_connection.do_find_one({'guild_id': guild_id}, collection_name)