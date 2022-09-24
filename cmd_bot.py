import datetime
from pprint import pp, pprint
import re
from lightbulb.ext import tasks
from typing import Sequence, Union
import hikari
import lightbulb
from SessionEvent import Session
import SessionTransformer
import GuildConfiguration
import SessionFactory
from Table import Table
from decouple import config

bot = lightbulb.BotApp(
    token=config('BOT_TOKEN'),
    help_slash_command=True,
)
tasks.load(bot)

doc_link = 'https://github.com/Malardrim/heraultquestbot#commandes'
doc_message = 'Voici le lien vers les instructions: ' + doc_link

@bot.listen(hikari.GuildJoinEvent)
async def invite_listener(event: hikari.GuildJoinEvent):
    for channel in event.channels:
        if isinstance(channel, hikari.GuildTextChannel):
            await bot.rest.create_message(channel, 'Merci pour l\'invit voici le lien de comment m\'utiliser :) ' + doc_link)
            await bot.rest.create_message(channel, 'N\'oubliez pas d\'utiliser la commande `/config` pour me configurer :)')
            return

async def fetch_sessions(guildId: str, full: bool = False):
    conf = await GuildConfiguration.get_config(guildId)
    channel = conf['channel_organisation']
    messages = await bot.rest.fetch_messages(channel)
    sessions = []
    for message in messages:
        if message.content is not None and message.content.startswith('Session du '):
            sessions.append(SessionTransformer.MessageToSession(message))
    if full == True:
        return sessions
    return sessions[-3:]


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
    tables = 0;
    if ctx.options.tables is not None:
        tables = int(ctx.options.tables)
    if re.match('[0-9]{2}/[0-9]{2}/[0-9]{4}', ctx.options.date) is None:
        await ctx.respond("Veuillez respecter le pattern de date\n" + doc_message)
        return
    session = SessionFactory.generate_session(ctx.options.date, ctx.options.hour, tables, ctx.options.complementary)
    await ctx.respond(SessionTransformer.session_to_message(session))



@create_session.set_error_handler
async def create_session_error_handler(event: lightbulb.CommandErrorEvent) -> bool:
    await event.context.respond("Une erreur est survenue")
    return True


@bot.command
@lightbulb.add_checks(check_session_is_created)
@lightbulb.add_checks(check_channel_inscriptions)
@lightbulb.option("session", "Session to join in", autocomplete=True)
@lightbulb.option("game_system", "Systeme de jeu", choices=['40k', 'AoS', 'KT', 'Infinity', 'Autre'])
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
    await event.context.respond("La session n'existe pas veuillez en choisir une valide " + doc_message)
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
    await event.context.respond("La session n'existe pas veuillez en choisir une valide " + doc_message)
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
    await event.context.respond("La session n'existe pas veuillez en choisir une valide " + doc_message)
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

@tasks.task(h=6, auto_start=True)
async def new_session_task():
    await generate_next_sessions()

async def generate_next_session_for_guild(guild_config: any, next_session: str):
    try:
        session = await get_session(guild_config['guild_id'], next_session)
        if session is None:
            time_now = (datetime.datetime.now()).strftime("%d/%m/%Y à %H:%M:%S")
            session = SessionFactory.generate_session(next_session, '19h', 8, 'Session générée en auto par le bot le: ' + time_now)
            session = SessionTransformer.session_to_message(session)
            await bot.rest.create_message(guild_config['channel_organisation'], session)
    except hikari.errors.ForbiddenError as forbidden:
        await GuildConfiguration.delete_config(guild_config['guild_id'])
        print('Guild deleted from bdd', forbidden)
    except:
        print('An unknown error occurred')

async def generate_next_sessions():
    next_session_date = (datetime.date.today() + datetime.timedelta( (4-datetime.date.today().weekday()) % 7 )).strftime("%d/%m/%Y")
    configs = await GuildConfiguration.get_all_configs()
    for config in configs:
        await generate_next_session_for_guild(config, next_session_date)

bot.run()
