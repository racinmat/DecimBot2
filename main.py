import asyncio
import os
import random

import aiohttp
import disnake
from disnake import Message, Intents
from disnake.ext import commands
from disnake.ext.commands import Bot, Context
from dotenv import load_dotenv

import decimdictionary as decdi

#TODO: logging
#TODO: make all stuff loadable modules

# preload all useful stuff
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEXT_SYNTH_TOKEN = os.getenv('TEXT_SYNTH_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')

class UnfilteredBot(Bot):
    """An overridden version of the Bot class that will listen to other bots."""

    async def process_commands(self, message):
        """Override process_commands to listen to bots."""
        ctx = await self.get_context(message)
        await self.invoke(ctx)

# add intents for bot and command prefix for classic command support
intents = Intents.all()
client = Bot(command_prefix=PREFIX, intents=intents)
connector = aiohttp.TCPConnector(ssl=False)

# on_ready event - happens when bot connects to Discord API
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


# constants
HELP = decdi.HELP
WARCRAFTY_CZ = decdi.WARCRAFTY_CZ
GMOD_CZ = decdi.GMOD_CZ
WOWKA_CZ = decdi.WOWKA_CZ
MOT_HLASKY = decdi.MOT_HLASKY
LINUX_COPYPASTA = decdi.LINUX_COPYPASTA

# useful functions/methods
async def batch_react(m, reactions: list):
    for reaction in reactions:
        await m.add_reaction(reaction)
    pass

# on_member_join - happens when a new member joins guild
@client.event
async def on_member_join(member: disnake.Member):
    welcome_channel = client.get_channel(decdi.WELCOMEPERO)
    await welcome_channel.send(f"""
Vítej, {member.mention}!
Prosím, přesuň se do <#1314388851304955904> a naklikej si role. Nezapomeň na roli Člen, abys viděl i ostatní kanály!
---
Please, go to the <#1314388851304955904> channel and select your roles. Don't forget the 'Člen'/Member role to see other channels!
                        """)
    pass

## Commands here ->
# Show all available commands
@client.command()
async def decimhelp(ctx):
    m = await ctx.send(HELP)
    await asyncio.sleep(10)
    # automoderation
    await ctx.message.delete()
    await m.delete()

# debug command/trolling
@client.command()
async def say(ctx, *args):
    if str(ctx.message.author) == 'SkavenLord58#0420':
        await ctx.message.delete()
        await ctx.send(f'{" ".join(args)}')
    else:
        print(f'{ctx.message.author} tried to use "say" command.')
        # await ctx.message.delete()

# poll creation, takes up to five arguments
@client.command()
async def poll(ctx, *args):
    poll_mess = f"Anketa: {args[0]}\n".replace("_", " ")
    m = await ctx.send("Creating poll... (If stuck, something failed horribly.)")
    try:
        poll_mess += f":one: = {args[1]}\n".replace("_", " ")
        await m.add_reaction("1️⃣")
        poll_mess += f":two: = {args[2]}\n".replace("_", " ")
        await m.add_reaction("2️⃣")
        poll_mess += f":three: = {args[3]}\n".replace("_", " ")
        await m.add_reaction("3️⃣")
        poll_mess += f":four: = {args[4]}\n".replace("_", " ")
        await m.add_reaction("4️⃣")
        poll_mess += f":five: = {args[5]}\n".replace("_", " ")
        await m.add_reaction("5️⃣")
    except Exception as exc:
        pass
    await m.edit(content=f"{poll_mess}")

# rolls a dice
@client.command()
async def roll(ctx, arg_range=None):
    range = None
    try:
        range = int(arg_range)
    except Exception as exc:
        pass

    if arg_range == "joint":
        await ctx.reply(f'https://youtu.be/LF6ok8IelJo?t=56')
    elif not range:
        await ctx.send(f'{random.randint(0, 100)} (Defaulted to 100d.)')
    elif type(range) is int and range > 0:
        await ctx.send(f'{random.randint(0, int(range))} (Used d{range}.)')
    else:
        await ctx.reply(f'Something\'s wrong. Check your syntax.')


# "twitter" functionality 
@client.slash_command(name = "tweet", description = "Posts a 'tweet' in #twitter-pero channel.", guild_ids=decdi.GIDS)
async def tweet(ctx, content: str, media: str = "null", anonym: bool = False):
    twitterpero = client.get_channel(decdi.TWITTERPERO)
    sentfrom = f"Sent from #{ctx.channel.name}"

    if anonym:
        random_city = "Void"
        random_name = "Jan Jelen"

        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get("https://randomuser.me//api") as api_call:
                    if api_call.status == 200:
                        result = (await api_call.json())["results"][0]
                        randomizer_opt = ["0","1","2","3","4"] # lazy way
                        randomizer_opt[0] = result["login"]["username"]
                        randomizer_opt[1] = result["email"].split("@")[0]
                        randomizer_opt[2] = result["login"]["password"] + str(result["dob"]["age"])
                        randomizer_opt[3] = result["gender"] + "goblin" + str(result["dob"]["age"])
                        randomizer_opt[4] = "lil" + result["location"]["country"].lower() + "coomer69"

                        random_name = f"@{randomizer_opt[random.randint(0, len(randomizer_opt) - 1)]}"
                        random_city = result["location"]["city"]
        except:
            pass

        embed = disnake.Embed(
            title=f"{random_name} tweeted:",
            description=f"{content}",
            color=disnake.Colour.dark_purple()
        )
        embed.set_thumbnail(url=result["picture"]["medium"])
        sentfrom = f"Sent from {random_city} (#{ctx.channel.name})"
    else:
        embed = disnake.Embed(
            title=f"{ctx.author.display_name} tweeted:",
            description=f"{content}",
            color=disnake.Colour.dark_purple()
        )
        embed.set_thumbnail(url=ctx.author.avatar)
    
    if media != "null":
        embed.set_image(url=media)
    embed.add_field(name=f"_", value=sentfrom, inline=True)
    await ctx.response.send_message(content="Tweet posted! 👍", ephemeral=True)
    m = await twitterpero.send(embed=embed)
    await batch_react(m, ["💜", "🔁", "⬇️", "💭", "🔗"])

    

@client.command()
async def ping(ctx):
    m = await ctx.send(f'Ping?')
    ping = int(str(m.created_at - ctx.message.created_at).split(".")[1]) / 1000
    await m.edit(content=f'Pong! Latency is {ping}ms. API Latency is {round(client.latency * 1000)}ms.')
    pass


@client.command()
async def yesorno(ctx, *args):
    answers = ("Yes.", "No.", "Perhaps.", "Definitely yes.", "Definitely no.")
    await ctx.reply(f'{answers[random.randint(0, len(answers) - 1)]}')
    pass


@client.command()
async def warcraft(ctx, *args):
    # automoderation
    await ctx.message.delete()
    # send z templaty
    if args:
        m = await ctx.send(WARCRAFTY_CZ.replace('{0}', f' v cca {args[0]}'))
    else:
        m = await ctx.send(WARCRAFTY_CZ.replace('{0}', ''))
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"])
    pass

@client.command()
async def wowko(ctx, *args):
    # automoderation
    await ctx.message.delete()
    # send z templaty
    if args:
        m = await ctx.send(WOWKA_CZ.replace('{0}', f' v cca {args[0]}').replace('{1}', f' v cca {args[1]}').replace('{2}', f' v cca {args[2]}'))
    else:
        m = await ctx.send(WOWKA_CZ.replace('{0}', ''))
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "☦️", "🇹", "🇭", "🇩", "🇴"])
    pass


@client.command()
async def gmod(ctx, *args):
    # automoderation
    await ctx.message.delete()
    # send z templaty
    if args:
        m = await ctx.send(GMOD_CZ.replace('{0}', f' v cca {args[0]}'))
    else:
        m = await ctx.send(GMOD_CZ.replace('{0}', ''))
    # přidání reakcí
    await batch_react(m, ["✅", "❎", "🤔", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "❓"])
    pass

@client.command()
async def today(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://national-api-day.herokuapp.com/api/today') as response:
            payload = await response.json()
            holidays: list[str] = payload.get("holidays", [])
            await ctx.reply(f'Today are following holiday: {", ".join(holidays)}')
    pass

@client.command()
async def fetchrole(ctx):
    roles = await ctx.guild.fetch_roles()
    await ctx.send(roles)

@client.slash_command(name = "createrolewindow", description = "Posts a role picker window.", guild_ids=decdi.GIDS)
@commands.default_member_permissions(administrator=True)
async def command(ctx):
    
    embed = disnake.Embed (
        title="Role picker",
        description="Here you can pick your roles:",
        color=disnake.Colour.light_gray(),)
    embed.add_field(name="Zde jsou role na přístup do různých 'pér'.\nDejte si člena, abyste viděli všude jinde.", value="_")
    

    gamingembed = disnake.Embed (
        title="Gaming Roles",
        description="Here you can pick your gaming tag roles:",
        color=disnake.Colour.dark_purple())
    gamingembed.add_field(name="Zde jsou role na získání tagovacích rolí na hry.", value="_")
    
    await ctx.response.send_message(content="Done!", ephemeral=True)


    await ctx.channel.send(
        embed=embed,
        components=[
            disnake.ui.Button(label="Člen", style=disnake.ButtonStyle.grey, custom_id="Člen", row=0),
            disnake.ui.Button(label="Pražák", style=disnake.ButtonStyle.green, custom_id="Pražák", row=1),
            disnake.ui.Button(label="Ostravák", style=disnake.ButtonStyle.green, custom_id="Ostravák", row=1),
            disnake.ui.Button(label="Brňák", style=disnake.ButtonStyle.green, custom_id="brnak", row=1),
            disnake.ui.Button(label="Carfag-péro", style=disnake.ButtonStyle.grey, custom_id="carfag", row=2),
        ]
    )
    await ctx.channel.send(
        embed=gamingembed,
        components=[
            disnake.ui.Button(label="Warcraft 3", style=disnake.ButtonStyle.blurple, custom_id="warcraft"),
            disnake.ui.Button(label="Wowko", style=disnake.ButtonStyle.blurple, custom_id="wowko"),
            disnake.ui.Button(label="Garry's Mod", style=disnake.ButtonStyle.blurple, custom_id="gmod"),
            disnake.ui.Button(label="Valorant", style=disnake.ButtonStyle.blurple, custom_id="valorant"),
            disnake.ui.Button(label="LoL", style=disnake.ButtonStyle.blurple, custom_id="lolko"),
            disnake.ui.Button(label="Dota 2", style=disnake.ButtonStyle.blurple, custom_id="dota2"),
            disnake.ui.Button(label="CS:GO", style=disnake.ButtonStyle.blurple, custom_id="csgo"),
            disnake.ui.Button(label="Sea of Thieves", style=disnake.ButtonStyle.blurple, custom_id="sea of thieves"),
            disnake.ui.Button(label="Kyoudai (Yakuza/Mahjong)", style=disnake.ButtonStyle.blurple, custom_id="kyoudai"),
            disnake.ui.Button(label="Minecraft", style=disnake.ButtonStyle.blurple, custom_id="minecraft"),
            disnake.ui.Button(label="Dark and Darker", style=disnake.ButtonStyle.blurple, custom_id="dark and darker"),
            disnake.ui.Button(label="Rainbow Six Siege", style=disnake.ButtonStyle.blurple, custom_id="duhová šestka"),
            disnake.ui.Button(label="Golf With Your Friends", style=disnake.ButtonStyle.blurple, custom_id="golfisti"),
            disnake.ui.Button(label="Civilisation V", style=disnake.ButtonStyle.blurple, custom_id="civky"),
            disnake.ui.Button(label="ROCK AND STONE (Deep rock Gal.)", style=disnake.ButtonStyle.blurple, custom_id="rockandstone"),
            disnake.ui.Button(label="Heroes of the Storm", style=disnake.ButtonStyle.blurple, custom_id="hots"),
            disnake.ui.Button(label="GTA V online", style=disnake.ButtonStyle.blurple, custom_id="gtaonline"),
            disnake.ui.Button(label="Warframe", style=disnake.ButtonStyle.blurple, custom_id="warframe"),
            disnake.ui.Button(label="Helldivers II", style=disnake.ButtonStyle.blurple, custom_id="helldivers"),
            disnake.ui.Button(label="Void Crew", style=disnake.ButtonStyle.blurple, custom_id="voidboys"),
            disnake.ui.Button(label="Finálníci (the Finals)", style=disnake.ButtonStyle.blurple, custom_id="thefinals"),
          
        ])

@client.listen("on_button_click")
async def listener(ctx: disnake.MessageInteraction):
    role_list = {
        "Člen": 804431648959627294,
        "warcraft": 871817685439234108,
        "gmod" : 951457356221394975,
        "valorant" : 991026818054225931,
        "kyoudai": 1031510557163008010,
        "lolko" : 994302892561399889,
        "dota2" : 994303445735587991,
        "csgo" : 994303566082740224,
        "sea of thieves": 994303863643451442,
        "duhová šestka": 1011212649704460378,
        "minecraft": 1049052005341069382,
        "dark and darker" : 1054111346733617222,
        "Ostravák": 988431391807131690,
        "Pražák" : 998636130511630386,
        "carfag" : 1057281159509319800,
        "golfisti": 1076931268555587645,
        "brnak": 1105227159712309391,
        "wowko": 1120426868697473024,
        "civky": 1070800908729995386,
        "rockandstone": 1107334623983312897,
        "hots": 1140376580800118835,
        "gtaonline": 1189322955063316551,
        "warframe": 1200135734590451834,
        "helldivers": 1228002980754751621,
        "voidboys": 1281326981878906931,
        "thefinals": 1242187454837035228,
    }
    if ctx.component.custom_id in role_list.keys():
        role_id = role_list[ctx.component.custom_id]
        role = ctx.guild.get_role(role_id)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` removed!", ephemeral=True)
        else:
            await ctx.author.add_roles(role)
            await ctx.response.send_message(content=f"Role `{ctx.component.custom_id}` added!", ephemeral=True)
    else:
        pass

@client.command()
async def cat(ctx, *args):
    try:
        if args.__len__() >= 2:
            w = args[0]
            h = args[1]
        else:
            w = random.randint(64,640)
            h = random.randint(64,640)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(f"https://placekitten.com/{w}/{h}") as api_call:
                if api_call.status == 200:
                    await ctx.send(f"https://placekitten.com/{w}/{h}")
                else:
                    await ctx.send("Oh nyo?!?! Something went ^w^ wwong?!!")
    except Exception as exc:
        print(f"Encountered exception:\n {exc}")
        await ctx.send("Oh nyo?!?! Something went ^w^ wwong?!!")

@client.command()
async def fox(ctx):
    try:
        await send_http_response(ctx, "https://randomfox.ca/floof/", "image", "Server connection error :( No fox image for you.")
    except Exception as exc:
        print(f"Caught exception:\n {exc}")

@client.command()
async def waifu(ctx, *args):
    try:
        if args and args[0] in ["sfw", "nsfw"]:
            if args[1]:
                url = f"https://api.waifu.pics/{args[0]}/{args[1]}"
            else:
                url = f"https://api.waifu.pics/{args[0]}/neko"
        else:
            url = f"https://api.waifu.pics/sfw/neko"
        await send_http_response(ctx, url, "url", "Server connection error :( No waifu image for you.")
    except Exception as exc:
        print(f"Caught exception:\n {exc}")


async def send_http_response(ctx: Context, url: str, resp_key: str, error_message: str) -> None:
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as api_call:
            if api_call.status == 200:
                await ctx.send((await api_call.json())[resp_key])
            else:
                await ctx.send(error_message)


@client.command()
async def autostat(ctx):
    m = ctx.message
    await m.reply("OK;")

# sends an xkcd comics
@client.command()
async def xkcd(ctx, *args):
    if args:
        await send_http_response(ctx, 'https://xkcd.com/' + args[0] + '/info.0.json', "img", "No such xkcd comics with this ID found.")
    else:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get('https://xkcd.com/info.0.json') as api_call:
                await ctx.send((await api_call.json())["img"])


# on message eventy
@client.event
async def on_message(m: Message):
    if not m.content:
        pass
    elif m.content[0] == PREFIX:
        # nutnost aby jely commandy    
        await UnfilteredBot.process_commands(client, m)
    elif str(m.author) != "DecimBOT 2.0#8467":
        if "negr" in m.content.lower():
            await m.add_reaction("🇳")
            # await m.add_reaction("🇪")
            # await m.add_reaction("🇬")
            # await m.add_reaction("🇷")
        if "based" in m.content:
            await m.add_reaction("👌")
        if  m.content.lower().startswith("hodný bot") or "good bot" in m.content.lower():
            await m.add_reaction("🙂")
        if  m.content.lower().startswith("zlý bot") or "bad bot" in m.content.lower() or \
        "naser si bote" in m.content.lower() or "si naser bote" in m.content.lower():
            await m.add_reaction("😢")
        if "drip" in m.content.lower():
            await m.add_reaction("🥶")
            await m.add_reaction("💦")
        if "windows" in m.content.lower():
            if random.randint(0, 4) == 2:
                await m.add_reaction("😔")
        if "debian" in m.content.lower():
            if random.randint(0, 4) == 2:
                await m.add_reaction("💜")
        if "všechno nejlepší" in m.content.lower():
            await m.add_reaction("🥳")
            await m.add_reaction("🎉")
        if "co jsem to stvořil" in m.content.lower() and m.author == 'SkavenLord58#0420':
            await m.reply("https://media.tenor.com/QRTVgLglL6AAAAAd/thanos-avengers.gif")
        if "atpro" in m.content.lower():
            await m.add_reaction("😥")
            await m.reply("To mě mrzí.")
        if "in a nutshell" in m.content.lower():
            await m.add_reaction("🌰")
        if "decim je negr" in m.content.lower():
            await m.channel.send("nn, ty seš")

client.run(TOKEN)
