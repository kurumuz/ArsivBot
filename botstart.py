#!/usr/bin/python3
import json
import os
import aiohttp
import aiofiles
import os.path
import subprocess
from pathlib import Path
import sys
import requests
import urllib.request
import discord
from discord.utils import get
from discord import Message, Member, Forbidden, Reaction, User, Role, Embed, Emoji
from discord.ext.commands import Bot, Context, UserConverter, CommandError, Converter
from requests import Response
prefix = "."
global dcheck
dcheck = 0
resimcount = 0

bot = Bot(command_prefix=prefix)
@bot.event
async def on_ready():
    init()
    print("Yaşıyorum ^^")
    print(bot.user.name + " olarak giriş yapıldı, id = " + bot.user.id)

@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return
    if not kayit_check(message):
        register(message)
    if await image_download(message):
        return
    global dcheck       
       
    file = await aiofiles.open("db/" + message.author.name + "/acheck", "r")
    acheck = await file.read()
    if acheck != "NULL":
        return await get_answer_image(message)
    if dcheck == 1: #TODO: kişiye özel olmalı
        return await selectDers(message)
    try:
        if message.content[0] == prefix:
            return await bot.process_commands(message)
    except IndexError:
        print("Yazısız mesaj!")

async def is_image(message: Message):
    i = 0
    if len(message.attachments) > 0:
        while(i != len(message.attachments)):
            if message.attachments[i]['filename'].split('.')[-1] in {'jpeg', 'png', 'jpg'}:
                return True
            else:
                print("resim yok")
                await bot.send_message(message.channel, "Geçersiz dosya biçimi. Lütfen sadece fotoğraf dosyaları gönderin. " + message.author.mention)
                return False

async def image_download(message: Message):

    file = open("db/" + message.author.name + "/ders", "r")
    dersargumani = file.read()
    file = await aiofiles.open("db/" + message.author.name + "/acheck", "r")
    acheck = await file.read()
    if dersargumani != "NULL" and acheck == "NULL":

        if await is_image(message):
            i = 0
            resimcount = len(message.attachments)
            print(str(resimcount) + " soru var")
            if not os.path.exists("db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/"):
                os.makedirs("db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/")
                file = await aiofiles.open("db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/db", "a+")
                await file.write("1")
                
            while (i != resimcount):
                file = await aiofiles.open("db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/db", "r+")
                sorucount = await file.readline()
                print(sorucount)
                url = message.attachments[i]['url']
                print(url)
                path = "db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/" + dersargumani + sorucount + ".jpg"
                await download_file(url, path)
                file = await aiofiles.open("db/" + message.author.name + "/Çözülmemiş/" + dersargumani + "/db", "w+")
                if os.path.isfile(path):
                    await file.write(str(int(sorucount) + 1))
                    #TODO: Liste
                    file.close()
                else:
                    await bot.send_message(message.channel, "İndirme sırasında hata!" + message.author.mention)
                await bot.send_message(message.channel, "Sorunuz " + dersargumani + sorucount + " adı ile kayıt edildi." + message.author.mention)
                i = i + 1
            return         

        if len(message.attachments) < 1:
            print("resim yok")
            return

async def download_file(url, path):
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()
                return

def kayit_check(message: Message):

    if os.path.exists("db/" + message.author.name):
        return True
    else:
        return False
    return

def register(message: Message):

    os.makedirs("db/" + message.author.name)
    file = open("db/" + message.author.name + "/otodb", "w+")
    file = open("db/" + message.author.name + "/manudb", "w+")
    file.write("1")
    file = open("db/" + message.author.name + "/ders", "w+")
    file.write("NULL")
    file = open("db/" + message.author.name + "/acheck", "w+")
    file.write("NULL")
    file = open("db/" + message.author.name + "/sudo", "w+")
    file.write("0")
    os.makedirs("db/" + message.author.name + "/Çözülmemiş/")
    os.makedirs("db/" + message.author.name + "/Çözülmüş/")
    file.close()

def init():
    if not os.path.exists("db"):
        os.makedirs("db")
        print("db klasörü oluşturuldu!")
    return

async def changeDers(message: Message, dersadi):
    file = await aiofiles.open("db/" + message.author.name + "/ders", "w+")
    await file.write(dersadi)
    return await bot.send_message(message.channel, "Ders " + dersadi + " olarak ayarlandı. " + message.author.mention)

async def selectDers(message: Message):
    global dcheck
    if "0" in message.content.split():
        dcheck = 0
        return await changeDers(message, "NULL")
    if "1" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Geometri")
    if "2" in message.content.split():
        dcheck = 0
        return await changeDers(message, "MatematikTYT")

    if "3" in message.content.split():
        dcheck = 0
        return await changeDers(message, "MatematikAYT")

    if "4" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Fizik")

    if "5" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Kimya")

    if "6" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Biyoloji")

    if "7" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Türkçe")

    if "8" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Coğrafya")

    if "9" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Felsefe")

    if "10" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Tarih")

    if "11" in message.content.split():
        dcheck = 0
        return await changeDers(message, "Din")
    
    else:
        return await bot.send_message(message.channel, "Lütfen listedeki derslerden birini giriniz")

    return

@bot.command(pass_context=True)
async def s(ctx, *args):
    if len(args) > 0:
        i = 0
        file = await aiofiles.open("db/" + ctx.message.author.name + "/ders", "r")
        dersargumani = await file.read()
        while(i != len(args)):
            path = "db/" + ctx.message.author.name + "/Çözülmemiş/" + dersargumani
            if os.path.exists(path):
                if len(str(args[i]).split('-')) == 2:
                    a = args[i].split('-')[0]
                    while (int(a) <= int(args[i].split('-')[1])):
                        if os.path.isfile(path + "/" + dersargumani + a + ".jpg"):
                            await bot.send_file(ctx.message.channel, path + "/" + dersargumani + a + ".jpg")
                            a = str(int(a) + 1)
                        else:
                            await bot.send_message(ctx.message.channel, dersargumani + a + " adında bir soru bulunamadı " + ctx.message.author.mention)
                i = i + 1
                if os.path.isfile(path + "/" + dersargumani + args[i] + ".jpg"):
                    await bot.send_file(ctx.message.channel, path + "/" + dersargumani + args[i] + ".jpg")          
                else:
                    await bot.send_message(ctx.message.channel, dersargumani + args[i] + " adında bir soru bulunamadı " + ctx.message.author.mention)

                if os.path.isfile("db/" + ctx.message.author.name + "/Çözülmüş/" + dersargumani + "/" + dersargumani + args[i] + ".jpg"):
                    await bot.send_file(ctx.message.channel, "db/" + ctx.message.author.name + "/Çözülmüş/" + dersargumani + "/" + dersargumani + args[i] + ".jpg")                 
                i = i + 1    
                
            else:
                i = i + 1
                await bot.send_message(ctx.message.channel, dersargumani + " dersine kayıtlı hiçbir soru yok." + ctx.message.author.mention)

            

    else:
        return await bot.send_message(ctx.message.channel, "Lütfen soru adı giriniz." + ctx.message.author.mention)
    return

async def get_answer_image(message: Message):
    if len(message.content) > 0:
        if message.content[0] == "i": #TODO: i'yi küçültüp bak.
            file = await aiofiles.open("db/" + message.author.name + "/acheck", "w")
            await bot.send_message(message.channel, "İptal edildi." + message.author.mention)
            return await file.write("NULL")

    if await is_image(message):
        file = await aiofiles.open("db/" + message.author.name + "/ders", "r")
        dersargumani = await file.read()
        file = await aiofiles.open("db/" + message.author.name + "/acheck", "r")
        acheck = await file.read()
        if not os.path.exists("db/" + message.author.name + "/Çözülmüş/" + dersargumani + "/"):
            os.makedirs("db/" + message.author.name + "/Çözülmüş/" + dersargumani + "/")
            file = await aiofiles.open("db/" + message.author.name + "/Çözülmüş/" + dersargumani + "/db", "a+")
            await file.write("1")
        url = message.attachments[0]['url']
        await download_file(url, "db/" + message.author.name + "/Çözülmüş/" + dersargumani + "/" + acheck)
        file = await aiofiles.open("db/" + message.author.name + "/acheck", "w")
        await file.write("NULL")
        return await bot.send_message(message.channel, "Çözümünüz " + acheck + " adı ile kayıt edildi." + message.author.mention)
    else:
        return await bot.send_message(message.channel, "Lütfen cevap fotoğrafını gönderin, iptal için iptal yazın." + message.author.mention)
    return

@bot.command(pass_context=True) #soruya cevap vermek veya çözülmüş işaretlemek için.
async def a(ctx, *args):
    file = await aiofiles.open("db/" + ctx.message.author.name + "/ders", "r")
    dersargumani = await file.read()
    path = "db/" + ctx.message.author.name + "/Çözülmemiş/" + dersargumani
    if dersargumani != "NULL" and len(args) == 1 and os.path.exists(path):
        if os.path.isfile(path + "/" + dersargumani + args[0] + ".jpg"):              
            await bot.send_file(ctx.message.channel, path + "/" + dersargumani + args[0] + ".jpg")
            await bot.send_message(ctx.message.channel, "bu soru için cevap gönderin, iptal için iptal yazın." + ctx.message.author.mention)
            acheck = dersargumani + args[0] + ".jpg"
            file = await aiofiles.open("db/" + ctx.message.author.name + "/acheck", "r+")
            await file.write(acheck)
        else:
            await bot.send_message(ctx.message.channel, dersargumani + args[0] + " adında bir soru bulunamadı" + ctx.message.author.mention)                                         
    return

@bot.command(pass_context=True)
async def d(ctx, *args):
    
    global dcheck
    if len(args) == 0 and dcheck == 0:
        dcheck = 1
        return await bot.send_message(ctx.message.channel, "```\nGeometri = 1\nMatematikTYT = 2\nMatematikAYT = 3\nFizik = 4\nKimya = 5\nBiyoloji = 6\nTürkçe = 7\nCoğrafya = 8\nFelsefe = 9\nTarih = 10\nDin = 11\n```")
            
    if len(ctx.message.attachments) > 0:
        print("bu ifadeyle aynı anda soru eklenemez.")
    if len(args) == 1:
        if args[0] == "l":
            return await bot.send_message(ctx.message.channel, "```\nGeometri = 1\nMatematikTYT = 2\nMatematikAYT = 3\nFizik = 4\nKimya = 5\nBiyoloji = 6\nTürkçe = 7\nCoğrafya = 8\nFelsefe = 9\nTarih = 10\nDin = 11\n```")
        elif args[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'}:
            dcheck = 0
            return await selectDers(ctx.message)
        else:
            print("geçersiz ders adı")
            return await bot.send_message(ctx.message.channel, "geçersiz ders adı. Lütfen geçerli bir ders adı giriniz. yardım için /yardim " + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "Lütfen tek bir argüman giriniz. " + ctx.message.author.mention)
    
        
@bot.command(pass_context=True)
async def hepsi(ctx, *args):
    if await sudo_check(ctx.message):
        i = 0
        file = await aiofiles.open("db/" + ctx.message.author.name + "/ders", "r")
        dersargumani = await file.read()
        kacTane=len(os.listdir("db/" + ctx.message.author.name + "/Çözülmemiş/" + dersargumani))
        while(i != kacTane-1):
            path = "db/" + ctx.message.author.name + "/Çözülmemiş/" + dersargumani
            if os.path.exists(path):
                if os.path.isfile(path + "/" + dersargumani +str(i+1) + ".jpg"):
                    await bot.send_file(ctx.message.channel, path + "/" + dersargumani + str(i+1) + ".jpg")
                else:
                    await bot.send_message(ctx.message.channel, dersargumani + str(i+1) + " adında bir soru bulunamadı" + ctx.message.author.mention)

                if os.path.isfile("db/" + ctx.message.author.name + "/Çözülmüş/" + dersargumani + "/" + dersargumani + str(i+1) + ".jpg"):
                    await bot.send_file(ctx.message.channel, "db/" + ctx.message.author.name + "/Çözülmüş/" + dersargumani + "/" + dersargumani + str(i+1) + ".jpg")
                i = i + 1

            else:
                i = i + 1
                await bot.send_message(ctx.message.channel, dersargumani + " dersine kayıtlı hiçbir soru yok." + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "Bu komutu kullanmanız için gereken yetkilere sahip değilsiniz." + ctx.message.author.mention)

async def sudo_check(message: Message):
    
    file = await aiofiles.open("db/" + message.author.name + "/sudo" , "r")
    sudo = await file.read()
    if sudo == "1":
        print("Kullanıcı " + message.author.name + " sudo yetkilerine sahip, izin verildi.")
        return True
    else:
        await bot.send_message(message.channel, message.author.mention + " sudo yetkilerine sahip değil, bu olay raporlanacak")
        return False        

@bot.group(pass_context=True)
async def sudo(ctx):
    if not await sudo_check(ctx.message):
        ctx.invoked_subcommand = None
        return
    if ctx.invoked_subcommand is None:
        await bot.send_message(ctx.message.channel, 'yanlış .sudo komutu girildi.')

@sudo.command(pass_context=True)
async def restart(ctx):
    
    process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
    await bot.send_message(ctx.message.channel, str(process.communicate()[0], "utf-8"))
    await bot.send_message(ctx.message.channel, 'Restarting...')
    os.execl("botstart.py", sys.argv[0])
    
tokenfile = open("db/token", "r")
token = tokenfile.read()
tokenfile.close()
bot.run(token)
