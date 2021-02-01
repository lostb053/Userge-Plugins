"""Last FM"""

# Copyright (C) 2020 BY USERGE-X.
# All rights reserved.
# Inspiration from @lastfmrobot <mainly> (owned by @dangou on telegram) and...
# @TheRealPhoenixBot(owned by @TheRealPhoenix on telegram and...
# github user as rsktg)
# Code re-written by @DeletedUser420 (telegram), github user as code-rgb

import asyncio

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from userge import Config, Message, get_collection, userge
from userge.lastfm import auth_, get_response, pcurl, ripimg, tglst, user
from userge.utils import rand_array

du = "https://last.fm/user/"


@userge.on_cmd(
    "toggleprofile",
    about={
        "header": "Toggle LastFM Profile",
        "description": "toggle lastfm profile to be shown or hidden",
        "usage": "{tr}toggleprofile on/off",
    },
)
async def toggle_lastfm_profile_(message: Message):
    """Toggle LastFM Profile"""
    if not message.input_str:
        return await message.edit("Please check `{tr}help toggleprofile`", del_in=5)
    in_ = message.input_str
    tgl = "Show" if in_ == "on" else "Hide" if in_ == "off" else ""
    await asyncio.gather(
        get_collection("CONFIGS").update_one(
            {"_id": "SHOW_LASTFM"},
            {"$set": {"on": tgl}},
            upsert=True,
        ),
    )
    await message.edit("`Settings updated`", del_in=5)


@userge.on_cmd(
    "lp",
    about={
        "header": "Get Lastfm now playing pic",
        "usage": "{tr}lp [lastfm username] (optional)",
    },
)
async def last_fm_pic_(message: Message):
    """Currently Playing"""
    query = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getrecenttracks",
        "user": query,
        "limit": 3,
        "extended": 1,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    view_data = (await get_response(params))[1]
    recent_song = view_data["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    querydisplay = f"[{query}]({du}{query})" if message.input_str else await user()
    if recent_song[0].get("@attr"):
        img = recent_song[0].get("image")[3].get("#text")
        if img in ripimg():
            img = rand_array(pcurl())
        rep = f"[\u200c]({img})**{querydisplay}** is currently listening to:\n"
        song_ = recent_song[0]
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"🎧  <code>{artist_name} - {song_name}</code>"
        if song_["loved"] != "0":
            rep += ", ♥️"
        gt = (
            (
                await get_response(
                    {
                        "method": "track.getInfo",
                        "track": song_name,
                        "artist": artist_name,
                        "api_key": Config.LASTFM_API_KEY,
                        "format": "json",
                    }
                )
            )[1]
        )["track"]["toptags"]["tag"]
        y = [i.replace(" ", "_").replace("-", "_") for i in [tg["name"] for tg in gt]]
        z = []
        z.append(k.lower()) for k in y if k in tglst() and k not in z
        neutags = " #".join(z[i] for i in range(min(len(z), 4)))
        if neutags != "":
            rep += f"\n#{neutags}"
        qry = "%20".join(
            (artist_name.replace(" ", "%20"), song_name.replace(" ", "%20"))
        )
        b = [
            [
                InlineKeyboardButton(
                    text="🎼YouTube",
                    url=f"https://www.youtube.com/results?search_query={qry}",
                ),
                InlineKeyboardButton(
                    text="🎶Spotify", url=f"https://open.spotify.com/search/{qry}"
                ),
            ]
        ]
        await message.edit(rep, reply_markup=InlineKeyboardMarkup(b))
    else:
        rep = f"**{querydisplay}** was listening to ...\n"
        playcount = view_data.get("recenttracks").get("@attr").get("total")
        for song_ in recent_song:
            song_name = song_["name"]
            artist_name = song_["artist"]["name"]
            rep += f"\n🎧  {artist_name} - {song_name}"
            if song_["loved"] != "0":
                rep += ", ♥️"
        rep += f"`\n\nTotal Scrobbles = {playcount}`"
        await message.edit(rep)


@userge.on_cmd(
    "linfo",
    about={
        "header": "Get Lastfm user info",
        "usage": "{tr}linfo [lastfm username] (optional)",
    },
)
async def last_fm_user_info_(message: Message):
    """Shows User Info"""
    query = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getInfo",
        "user": query,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    lastuser = (await get_response(params))[1]["user"]
    lastimg = lastuser.get("image")[3].get("#text")
    result = ""
    if lastimg:
        result += f"[\u200c]({lastimg})"
    querydisplay = f"[{query}]({du}{query})" if message.input_str else await user()
    result += f"LastFM User Info for **{querydisplay}**:\n**User:** {query}\n"
    name = lastuser.get("realname")
    if name != "":
        result += f" 🔰 **Name:** {name}\n"
    result += f" 🎵 **Total Scrobbles:** {lastuser['playcount']}\n"
    country = lastuser.get("country")
    if country != "None":
        result += f" 🌍 **Country:** {country}\n"
    await message.edit(result)


@userge.on_cmd(
    "pc",
    about={
        "header": "Get Lastfm user playcount",
        "usage": "{tr}pc [lastfm username] (optional)",
    },
)
async def last_pc_(message: Message):
    """Shows Playcount"""
    query = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getInfo",
        "user": query,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    lastuser = (await get_response(params))[1]["user"]
    querydisplay = f"[{query}]({du}{query})" if message.input_str else await user()
    result = f"**{querydisplay}'s** playcount is:\n{lastuser['playcount']}"
    await message.edit(result, disable_web_page_preview=True)


@userge.on_cmd(
    "loved",
    about={
        "header": "Get Lastfm Loved Tracks",
        "usage": "{tr}loved [lastfm username] (optional)",
    },
)
async def last_fm_loved_tracks_(message: Message):
    """Shows Liked Songs"""
    query = message.input_str or Config.LASTFM_USERNAME
    params = {
        "method": "user.getlovedtracks",
        "limit": 20,
        "user": query,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    tracks = (await get_response(params))[1]["lovedtracks"]["track"]
    if len(tracks) == 0:
        return await message.edit("You Don't have any Loved tracks yet.")
    querydisplay = f"[{query}]({du}{query})" if message.input_str else await user()
    rep = f"**Favourite (♥️) Tracks for {querydisplay}**"
    for song_ in tracks:
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n🎧  **{artist_name}** - {song_name}"
    await message.edit(rep, disable_web_page_preview=True)


@userge.on_cmd(
    "hp",
    about={
        "header": "Get Upto 20 recently played LastFm Songs",
        "usage": "{tr}hp [lastFM username] (optional)",
    },
)
async def last_fm_played_(message: Message):
    """Shows Recently Played Songs"""
    query = message.input_str or Config.LASTFM_USERNAME
    querydisplay = f"[{query}]({du}{query})" if message.input_str else await user()
    params = {
        "method": "user.getrecenttracks",
        "limit": 20,
        "extended": 1,
        "user": query,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    recent_song = (await get_response(params))[1]["recenttracks"]["track"]
    if len(recent_song) == 0:
        return await message.err("No Recent Tracks found", del_in=5)
    rep = f"**{querydisplay}** recently played 🎵 songs:\n"
    for song_ in recent_song:
        song_name = song_["name"]
        artist_name = song_["artist"]["name"]
        rep += f"\n🎧  {artist_name} - {song_name}"
        if song_["loved"] != "0":
            rep += ", ♥️"
    await message.edit(rep, disable_web_page_preview=True)


@userge.on_cmd(
    "loveit",
    about={
        "header": "love recently playing song",
        "usage": "{tr}loveit",
    },
)
async def last_fm_played_(message: Message):
    """Loves Currently Playing Song"""
    await message.edit("Loving Currently Playing...")
    params = {
        "method": "user.getrecenttracks",
        "limit": 2,
        "user": Config.LASTFM_USERNAME,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    recent_song = (await get_response(params))[1]["recenttracks"]["track"]
    if len(recent_song) == 0 or not recent_song[0].get("@attr"):
        return await message.err("No Currently Playing Track found", del_in=10)
    img = recent_song[0].get("image")[3].get("#text")
    if img in ripimg():
        img = rand_array(pcurl())
    song_ = recent_song[0]
    anm = song_["artist"]["#text"]
    snm = song_["name"]
    auth_().get_track(anm, snm).love()
    await message.edit(
        f"Loved currently playing track...\n`{anm} - {snm}` [\u200c]({img})"
    )


@userge.on_cmd(
    "unloveit",
    about={
        "header": "unlove recently playing song",
        "usage": "{tr}unloveit",
    },
)
async def last_fm_played_(message: Message):
    """UnLoves Currently Playing Song"""
    await message.edit("UnLoving Currently Playing...")
    params = {
        "method": "user.getrecenttracks",
        "limit": 2,
        "user": Config.LASTFM_USERNAME,
        "api_key": Config.LASTFM_API_KEY,
        "format": "json",
    }
    recent_song = (await get_response(params))[1]["recenttracks"]["track"]
    if len(recent_song) == 0 or not recent_song[0].get("@attr"):
        return await message.err("No Currently Playing Track found", del_in=10)
    img = recent_song[0].get("image")[3].get("#text")
    if img in ripimg():
        img = rand_array(pcurl())
    song_ = recent_song[0]
    anm = song_["artist"]["#text"]
    snm = song_["name"]
    auth_().get_track(anm, snm).unlove()
    await message.edit(
        f"UnLoved currently playing track...\n`{anm} - {snm}` [\u200c]({img})"
    )


# The following code won't return actual compatibility as available on site
# but is basically similar to @lastfmrobot's compat cmd (just similar not same)
@userge.on_cmd(
    "compat",
    about={
        "header": "Compat",
        "description": "check music compat level with other lastfm users",
        "usage": """{tr}compat lastfmusername
        or
        {tr}compat lastfmusername1|lastfmusername2
        """,
    },
)
async def lastfm_compat_(message: Message):
    """Shows Music Compatibility"""
    if "|" in message.input_str:
        us1, us2 = message.input_str.split("|")
        display = f"**[{us1}]({du}{us1})** and **[{us2}]({du}{us2})**"
    elif message.input_str:
        us1, us2 = Config.LASTFM_USERNAME, message.input_str
        display = f"**{await user()}** and **[{us2}]({du}{us2})**"
    else:
        return await message.edit("Please check `{tr}help Compat`")
    ta1 = (
        await get_response(
            {
                "method": "user.getTopArtists",
                "user": us1,
                "limit": 500,
                "api_key": Config.LASTFM_API_KEY,
                "format": "json",
            }
        )
    )[1]["topartists"]["artist"]
    ta2 = (
        await get_response(
            {
                "method": "user.getTopArtists",
                "user": us2,
                "limit": 500,
                "api_key": Config.LASTFM_API_KEY,
                "format": "json",
            }
        )
    )[1]["topartists"]["artist"]
    ad1, ad2 = [n["name"] for n in ta1], [n["name"] for n in ta2]
    comart = [value for value in ad2 if value in ad1]
    compat = min((len(comart) * 100 / 40), 100)
    disartlst = {comart[r] for r in range(min(len(comart), 5))}
    disart = ", ".join(disartlst)
    rep = f"{display} both listen to __{disart}__...\nMusic Compatibility is **{compat}%**"
    await message.edit(rep, disable_web_page_preview=True)
