import hikari
import re

bot = hikari.GatewayBot(token='MTAxNTYxOTAzOTgyNzA4NzQwMA.G1vSc7.2uOBTz2Pmxd557_y_UEvO7cWlcuHylULQ-6EyQ')

async def successMessageTrigger(message) -> None:
    channels = await bot.rest.fetch_guild_channels(message.guild_id)
    for channel in channels:
        if isinstance(channel, hikari.GuildTextChannel) and channel.name == "test-salon-orga":
            orgaChannel = channel
    if orgaChannel is None:
        await message.add_reaction(":X:")
        return
    try:
        match = re.search("(([0-9]{2}\/){2}[0-9]{4})", message.content).group(1)
    except AttributeError:
        await message.add_reaction("💀")
        return
    orgaMessages = await bot.rest.fetch_messages(orgaChannel)
    for msg in orgaMessages:
        if msg.content.startswith("Session du " + match + ":" ):
            orgaMessage = msg
    if orgaMessage is None:
        return
    tables = [];
    lines = orgaMessage.content.split('\n');
    for line in lines:
        if line.startswith('- Table'):
            tables.append(line)

    await message.add_reaction("👌")


async def failureMessageTrigger(message) -> None:
    pins = await bot.rest.fetch_pins(message.channel_id)
    templateMessage = pins[0];
    await message.add_reaction("💀")
    await message.respond("Le message n'a pas le bon format\n" + "Pour rappel voici le format à suivre: ```" + templateMessage.content + "```");

@bot.listen()
async def ping(event: hikari.GuildMessageCreateEvent) -> None:
    if event.is_bot or not event.content:
        return
    if re.search("^([0-9]{2}\/){2}[0-9]{4}\s?- 40k (-.*){3}$", event.content):
        await successMessageTrigger(event.message)
    else:
        await failureMessageTrigger(event.message)

bot.run()