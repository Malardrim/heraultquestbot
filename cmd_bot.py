import datetime
import re
from typing import Sequence, Union
import hikari
import lightbulb
from SessionEvent import Session
import SessionTransformer
import GuildConfiguration
from Table import Table
from decouple import config

bot = lightbulb.BotApp(
    token=config('BOT_TOKEN'),
    help_slash_command=True,
)


async def fetch_sessions(guildId: str):
    conf = await GuildConfiguration.get_config(guildId)
    channel = conf['channel_organisation']
    messages = await bot.rest.fetch_messages(channel)
    sessions = []
    for message in messages:
        if message.content.startswith('Session du '):
            sessions.append(SessionTransformer.MessageToSession(message))
    return sessions


async def get_session(guild_id: str, name: str) -> Session:
    sessions = await fetch_sessions(guild_id)
    for session in sessions:
        if session.date == name:
            return session
    return None


@lightbulb.Check
async def check_session_is_created(context: lightbulb.Context) -> bool:
    sessions = await fetch_sessions(context.guild_id)
    for session in sessions:
        if session.date == context.options.session:
            return True
    return False


@lightbulb.Check
async def check_channel_inscriptions(context: lightbulb.Context) -> bool:
    conf = await GuildConfiguration.get_config(context.guild_id)
    return (context.channel_id == conf['channel_inscription'])


@lightbulb.Check
async def check_channel_organisation(context: lightbulb.Context) -> bool:
    conf = await GuildConfiguration.get_config(context.guild_id)
    return (context.channel_id == conf['channel_organisation'])


@bot.command
@lightbulb.add_checks(check_channel_organisation)
@lightbulb.option("date", "Date to participate", type=datetime.datetime)
@lightbulb.option("hour", "Starting hour", type=str)
@lightbulb.option("tables", "Number of tables available", type=int)
@lightbulb.option("complementary", "Infos complementaires de la session", type=str, default=None)
@lightbulb.command("create_session", "Creates a session for some day")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_session(ctx: lightbulb.Context) -> None:
    response = "Session du " + ctx.options.date + \
        " a partir de " + ctx.options.hour + "\n"
    if ctx.options.tables is not None:
        for tableNb in range(int(ctx.options.tables)):
            response += "- Table " + str(tableNb + 1) + ":\n"
        if ctx.options.complementary is not None:
            response += '\n***' + ctx.options.complementary + '***'
    await ctx.respond(response)


@create_session.set_error_handler
async def create_session_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    await event.context.respond("Une erreur est survenue")
    return True


@bot.command
@lightbulb.add_checks(check_session_is_created)
@lightbulb.add_checks(check_channel_inscriptions)
@lightbulb.option("session", "Session to join in", autocomplete=True)
@lightbulb.option("game_system", "Systeme de jeu", choices=['40k', 'AoS', 'KT', 'Autre'])
@lightbulb.option("game_type", "Type de jeu", choices=['1v1', '2v2', 'FFA', 'Autre'])
@lightbulb.option("game_size", "Taille de la partie")
@lightbulb.option("participants", "Participants")
@lightbulb.option("table", "table selected", default=None, type=int)
@lightbulb.command("inscription", "Inscription a une session")
@lightbulb.implements(lightbulb.SlashCommand)
async def inscription(ctx: lightbulb.Context) -> None:
    session = await get_session(ctx.guild_id, ctx.options.session)
    if ctx.options.table is not None:
        table = session.find_table(str(ctx.options.table))
        if table is None:
            await ctx.respond("La table n'existe pas")
            return
        if table.content is not None and table.content != '':
            await ctx.respond("La table demandée est remplie veuillez en choisir une autre")
            return
    else:
        table = session.first_empty_table()
        if table is None:
            await ctx.respond("La session est remplie!")
            return
    table.content = ctx.options.game_system + ' - ' + ctx.options.game_type + \
        ' - ' + ctx.options.game_size + ' - ' + ctx.options.participants
    await session.message.edit(SessionTransformer.session_to_message(session))
    await ctx.respond("Inscription reussie!!")


@inscription.set_error_handler
async def inscription_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    await event.context.respond("La session n'existe pas veuillez en choisir une valide")
    return True


@inscription.autocomplete("session")
async def session_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction
                               ) -> Union[str, Sequence[str], hikari.CommandChoice, Sequence[hikari.CommandChoice]]:
    sessions = await fetch_sessions(inter.guild_id)
    result = []
    for session in sessions:
        result.append(session.date)
    return result


@bot.command
@lightbulb.option("channel_organisation", "Channel to be used to post organization settings", default=None, type=hikari.TextableGuildChannel)
@lightbulb.option("channel_inscriptions", "Only channel allowed to run the incription command", default=None, type=hikari.TextableGuildChannel)
@lightbulb.command("config", "Mise en place/modification des configurations")
@lightbulb.implements(lightbulb.SlashCommand)
async def configuration_command(ctx: lightbulb.Context) -> None:
    orga_channel = ctx.options.channel_organisation.id if ctx.options.channel_organisation is not None else None
    inv_channel = ctx.options.channel_inscriptions.id if ctx.options.channel_inscriptions is not None else None
    config = await GuildConfiguration.update_guild_configuration(ctx.guild_id, orga_channel, inv_channel)
    inv_channel = await ctx.bot.rest.fetch_channel(config['channel_inscription'])
    await ctx.respond('Channel organisation: <#' + str(config['channel_organisation']) + '>\nChannel inscriptions: <#' + str(config['channel_inscription']) + '>')


@bot.command
@lightbulb.add_checks(check_session_is_created)
@lightbulb.add_checks(check_channel_organisation)
@lightbulb.option("table", "Identifiant de la table à ajouter")
@lightbulb.option("session", "Session a mettre à jour", autocomplete=True)
@lightbulb.command("add_table_session", "Ajout d'une table a une session")
@lightbulb.implements(lightbulb.SlashCommand)
async def add_table_session(ctx: lightbulb.Context) -> None:
    session = await get_session(ctx.guild_id, ctx.options.session)
    table = session.find_table(str(ctx.options.table))
    if table is not None:
        await ctx.respond("La table existe déjà")
        return
    table = Table(str(ctx.options.table), '')
    session.tables.append(table)
    await session.message.edit(SessionTransformer.session_to_message(session))
    await ctx.respond('Table ajoutée correctement')


@add_table_session.set_error_handler
async def add_table_session_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    await event.context.respond("La session n'existe pas veuillez en choisir une valide")
    return True


@add_table_session.autocomplete("session")
async def add_table_session_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction
                                         ) -> Union[str, Sequence[str], hikari.CommandChoice, Sequence[hikari.CommandChoice]]:
    return await session_autocomplete(opt, inter)


@bot.command
@lightbulb.add_checks(check_session_is_created)
@lightbulb.add_checks(check_channel_organisation)
@lightbulb.option("table", "Identifiant de la table à enlever")
@lightbulb.option("session", "Session a mettre à jour", autocomplete=True)
@lightbulb.command("remove_table_session", "Enlever une table a une session")
@lightbulb.implements(lightbulb.SlashCommand)
async def remove_table_session(ctx: lightbulb.Context) -> None:
    session = await get_session(ctx.guild_id, ctx.options.session)
    removed = session.remove_table(str(ctx.options.table))
    if removed == False:
        await ctx.respond("La table n'éxiste pas")
        return
    await session.message.edit(SessionTransformer.session_to_message(session))
    await ctx.respond('Table enlevée correctement')


@remove_table_session.set_error_handler
async def remove_table_session_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    await event.context.respond("La session n'existe pas veuillez en choisir une valide")
    return True


@remove_table_session.autocomplete("session")
async def remove_table_session_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction
                                            ) -> Union[str, Sequence[str], hikari.CommandChoice, Sequence[hikari.CommandChoice]]:
    return await session_autocomplete(opt, inter)


@bot.command
@lightbulb.add_checks(check_session_is_created)
@lightbulb.option("table", "Identifiant de la table à enlever")
@lightbulb.option("session", "Session a mettre à jour", autocomplete=True)
@lightbulb.command("unsuscribe_session", "Enlever une table a une session")
@lightbulb.implements(lightbulb.SlashCommand)
async def unsuscribe_session(ctx: lightbulb.Context) -> None:
    session = await get_session(ctx.guild_id, ctx.options.session)
    table = session.find_table(str(ctx.options.table))
    if table is None:
        await ctx.respond("La table n'éxiste pas")
        return
    if table.content is None or re.search(str(ctx.user.id), table.content) is None:
        await ctx.respond("Seul un des inscrits peut désinscrire une table")
        return
    table.content = ''
    await session.message.edit(SessionTransformer.session_to_message(session))
    await ctx.respond('Table enlevée correctement')


@unsuscribe_session.autocomplete("session")
async def unsuscribe_session_autocomplete(opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction
                                          ) -> Union[str, Sequence[str], hikari.CommandChoice, Sequence[hikari.CommandChoice]]:
    return await session_autocomplete(opt, inter)

bot.run()
