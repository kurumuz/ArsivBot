#!/usr/bin/python3
import json
import os
import aiohttp
import aiofiles
import os.path
import subprocess
import re
import sqlite3
from pathlib import Path
import sys
import requests
import urllib.request
import discord
from discord.utils import get
from discord import Message, Member, Forbidden, Reaction, User, Role, Embed, Emoji
from discord.ext.commands import Bot, Context, UserConverter, CommandError, Converter
from requests import Response
global database
database = sqlite3.connect("db/database")
prefix = "."
resimcount = 0
#dersargumani çok kullanıldığı için on_message fonksiyonundan diğer fonksiyonlara geçirebiliriz direk.
bot = Bot(command_prefix=prefix)
@bot.event
async def on_ready():
    init()
    print("Yaşıyorum ^^")
    print(bot.user.name + " olarak giriş yapıldı, id = " + bot.user.id)

@bot.event
async def on_message(message: Message):
    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"
    if message.author == bot.user:
        return
    
    register(message)
    
    if await image_download(message):
        return   
    
    cursor.execute(f"SELECT acheck FROM users WHERE username LIKE {user}")   
    acheck = cursor.fetchone()[0]

    cursor.execute(f"SELECT ncheck FROM users WHERE username LIKE {user}")   
    ncheck = cursor.fetchone()[0]

    cursor.execute(f"SELECT dcheck FROM users WHERE username LIKE {user}")   
    dcheck = cursor.fetchone()[0]

    if ncheck != "NULL":
        return await get_note_image(message)
    if acheck != "NULL":
        return await get_answer_image(message)
    if dcheck == "1": #TODO: kişiye özel olmalı
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
                print(f"{message.author}: {message.content}")
                await bot.send_message(message.channel, "Geçersiz dosya biçimi. Lütfen sadece fotoğraf dosyaları gönderin. " + message.author.mention)
                return False

async def image_download(message: Message):

    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    cursor.execute(f"SELECT acheck FROM users WHERE username LIKE {user}")   
    acheck = cursor.fetchone()[0]
    cursor.execute(f"SELECT ncheck FROM users WHERE username LIKE {user}")   
    ncheck = cursor.fetchone()[0]
    if dersargumani != "NULL" and acheck == "NULL" and ncheck == "NULL":

        if await is_image(message):
            i = 0
            resimcount = len(message.attachments)
            print(str(resimcount) + " soru var")
            if not os.path.exists("db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/"):
                os.makedirs("db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/")
                file = await aiofiles.open("db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/db", "a+")
                await file.write("1")
                await file.close()
            while (i != resimcount):
                file = await aiofiles.open("db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/db", "r+")
                sorucount = await file.readline()
                print(sorucount)
                url = message.attachments[i]['url']
                print(url)
                path = "db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/" + dersargumani + sorucount + ".jpg"
                await download_file(url, path)
                file = await aiofiles.open("db/" + str(message.author) + "/Çözülmemiş/" + dersargumani + "/db", "w+")
                if os.path.isfile(path):
                    await file.write(str(int(sorucount) + 1))
                    #TODO: Liste
                    await file.close()
                else:
                    await bot.send_message(message.channel, "İndirme sırasında hata!" + message.author.mention)
                await bot.send_message(message.channel, "Sorunuz " + dersargumani + sorucount + " adı ile kayıt edildi." + message.author.mention)
                i = i + 1
            return         

        if len(message.attachments) < 1:
            print(f"{message.author}: {message.content}")
            return

async def download_file(url, path):
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, mode='wb')
                await f.write(await resp.read())
                await f.close()
                return

def register(message: Message):
    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"
    cursor.execute(f"SELECT id, dcheck FROM users WHERE username LIKE {user}")
    result = cursor.fetchone()[0]
    if type(result) == NoneType:
        cursor.execute('''INSERT INTO users(username, dcheck, acheck, ncheck, ders, sudo)
                VALUES(?,?,?,?,?,?)''', (str(message.author), "0", "NULL", "NULL", "NULL", "0"))
        database.commit()
        if not os.path.exists("db/" + str(message.author)):
            os.makedirs("db/" + str(message.author))
        if not os.path.exists("db/" + str(message.author) + "/Çözülmemiş/"):
            os.makedirs("db/" + str(message.author) + "/Çözülmemiş/")
        if not os.path.exists("db/" + str(message.author) + "/Notlar/"):
            os.makedirs("db/" + str(message.author) + "/Notlar/")
        if not os.path.exists("db/" + str(message.author) + "/Çözülmüş/"):
            os.makedirs("db/" + str(message.author) + "/Çözülmüş/")


def init():
    if not os.path.exists("db"):
        os.makedirs("db")
        print("db klasörü oluşturuldu!")
    global database
    cursor = database.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT,
                            dcheck TEXT, acheck TEXT, ncheck Text, ders TEXT, sudo TEXT)
                            ''')
    return

async def changeDers(message: Message, dersadi):
    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"
    cursor.execute(f"UPDATE users SET ders = '{dersadi}' WHERE username LIKE {user}")
    database.commit()
    return await bot.send_message(message.channel, "Ders " + dersadi + " olarak ayarlandı. " + message.author.mention)

async def selectDers(message: Message):

    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"
    if "0" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "NULL")
    if "1" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Geometri")
    if "2" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "MatematikTYT")

    if "3" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "MatematikAYT")

    if "4" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Fizik")

    if "5" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Kimya")

    if "6" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Biyoloji")

    if "7" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Türkçe")

    if "8" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Coğrafya")

    if "9" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Felsefe")

    if "10" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Tarih")

    if "11" in message.content.split():
        cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
        database.commit()
        return await changeDers(message, "Din")
    
    else:
        return await bot.send_message(message.channel, "Lütfen listedeki derslerden birini giriniz")

    return

@bot.command(pass_context=True)
async def s(ctx, *args):
    if len(args) > 0:
        i = 0
        global database
        cursor = database.cursor()
        user = f"'%{str(ctx.message.author)}%'"
        cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
        dersargumani = cursor.fetchone()[0]
        while(i != len(args)):
            path = "db/" + str(ctx.message.author) + "/Çözülmemiş/" + dersargumani
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

                if os.path.isfile("db/" + str(ctx.message.author) + "/Çözülmüş/" + dersargumani + "/" + dersargumani + args[i] + ".jpg"):
                    await bot.send_file(ctx.message.channel, "db/" + str(ctx.message.author) + "/Çözülmüş/" + dersargumani + "/" + dersargumani + args[i] + ".jpg")                 
                i = i + 1    
                
            else:
                i = i + 1
                await bot.send_message(ctx.message.channel, dersargumani + " dersine kayıtlı hiçbir soru yok." + ctx.message.author.mention)

            

    else:
        return await bot.send_message(ctx.message.channel, "Lütfen soru adı giriniz." + ctx.message.author.mention)
    return

async def get_answer_image(message: Message):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    if len(message.content) > 0:
        if message.content[0] == "i": #TODO: i'yi küçültüp bak.
            cursor.execute(f"UPDATE users SET acheck = 'NULL' WHERE username LIKE {user}")
            database.commit()
            await bot.send_message(message.channel, "İptal edildi." + message.author.mention)
            return

    if await is_image(message):
        cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
        dersargumani = cursor.fetchone()[0]
        cursor.execute(f"SELECT acheck FROM users WHERE username LIKE {user}")
        acheck = cursor.fetchone()[0]
        if not os.path.exists("db/" + str(message.author) + "/Çözülmüş/" + dersargumani + "/"):
            os.makedirs("db/" + str(message.author) + "/Çözülmüş/" + dersargumani + "/")
        url = message.attachments[0]['url']
        await download_file(url, "db/" + str(message.author) + "/Çözülmüş/" + dersargumani + "/" + acheck)
        file = await aiofiles.open("db/" + str(message.author) + "/acheck", "w")
        cursor.execute(f"UPDATE users SET acheck = 'NULL' WHERE username LIKE {user}")
        database.commit()
        return await bot.send_message(message.channel, "Çözümünüz " + acheck + " adı ile kayıt edildi." + message.author.mention)
    else:
        return await bot.send_message(message.channel, "Lütfen cevap fotoğrafını gönderin, iptal için iptal yazın." + message.author.mention)
    return

async def get_note_image(message: Message):
    global database
    cursor = database.cursor()
    user = f"'%{str(message.author)}%'"    
    if len(message.content) > 0:
        if message.content[0].lower() == "i": #TODO: i'yi küçültüp bak.
            await bot.send_message(message.channel, "İptal edildi." + message.author.mention)
            cursor.execute(f"UPDATE users SET ncheck = 'NULL' WHERE username LIKE {user}")
            database.commit()
            return
        
    if await is_image(message):
        cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
        dersargumani = cursor.fetchone()[0]
        cursor.execute(f"SELECT ncheck FROM users WHERE username LIKE {user}")
        ncheck = cursor.fetchone()[0]
        url = message.attachments[0]['url']
        await download_file(url, "db/" + str(message.author) + "/Notlar/" + dersargumani + "/" + ncheck),
        cursor.execute(f"UPDATE users SET ncheck = 'NULL' WHERE username LIKE {user}")
        database.commit()
        return await bot.send_message(message.channel, "Notunuz " + ncheck + " adı ile kayıt edildi." + message.author.mention)
    else:
        return await bot.send_message(message.channel, "Lütfen cevap fotoğrafını gönderin, iptal için iptal yazın." + message.author.mention)
    return


@bot.command(pass_context=True) #soruya cevap vermek veya çözülmüş işaretlemek için.
async def a(ctx, *args):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    path = "db/" + str(ctx.message.author) + "/Çözülmemiş/" + dersargumani
    if dersargumani != "NULL" and len(args) == 1 and os.path.exists(path):
        if os.path.isfile(path + "/" + dersargumani + args[0] + ".jpg"):              
            await bot.send_file(ctx.message.channel, path + "/" + dersargumani + args[0] + ".jpg")
            await bot.send_message(ctx.message.channel, "bu soru için cevap gönderin, iptal için iptal yazın." + ctx.message.author.mention)
            acheck = dersargumani + args[0] + ".jpg"
            cursor.execute(f"UPDATE users SET acheck = {acheck} WHERE username LIKE {user}")
            database.commit()
        else:
            await bot.send_message(ctx.message.channel, dersargumani + args[0] + " adında bir soru bulunamadı" + ctx.message.author.mention)                                         
    return

@bot.command(pass_context=True)
async def d(ctx, *args):
    
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT dcheck FROM users WHERE username LIKE {user}")
    dcheck = cursor.fetchone()[0]

    if len(args) == 0 and dcheck == "0":
        cursor.execute(f"UPDATE users SET dcheck = '1' WHERE username LIKE {user}")
        database.commit()
        return await bot.send_message(ctx.message.channel, "```\nGeometri = 1\nMatematikTYT = 2\nMatematikAYT = 3\nFizik = 4\nKimya = 5\nBiyoloji = 6\nTürkçe = 7\nCoğrafya = 8\nFelsefe = 9\nTarih = 10\nDin = 11\n```")
            
    if len(ctx.message.attachments) > 0:
        print("bu ifadeyle aynı anda soru eklenemez.")
    if len(args) == 1:
        if args[0] == "l":
            return await bot.send_message(ctx.message.channel, "```\nGeometri = 1\nMatematikTYT = 2\nMatematikAYT = 3\nFizik = 4\nKimya = 5\nBiyoloji = 6\nTürkçe = 7\nCoğrafya = 8\nFelsefe = 9\nTarih = 10\nDin = 11\n```")
        elif args[0] in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'}:
            cursor.execute(f"UPDATE users SET dcheck = '0' WHERE username LIKE {user}")
            database.commit()
            return await selectDers(ctx.message)
        else:
            print("geçersiz ders adı")
            return await bot.send_message(ctx.message.channel, "geçersiz ders adı. Lütfen geçerli bir ders adı giriniz. yardım için /yardim " + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "Lütfen tek bir argüman giriniz. " + ctx.message.author.mention)

@bot.group(pass_context=True)
async def n(ctx):
    if ctx.invoked_subcommand is None:
        await bot.send_message(ctx.message.channel, 'yanlış .n komutu girildi.')

@n.command(pass_context=True)
async def ekle(ctx, *args):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    
    if not os.path.exists("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/"):
        os.makedirs("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/")
        
    if len(args) > 1:
        if args[0] == "foto":
            imname = args[1] + ".jpg"
            cursor.execute(f"UPDATE users SET ncheck = '{imname}' WHERE username LIKE {user}")
            database.commit()
            return await bot.send_message(ctx.message.channel, "Lütfen " + args[1] + " fotoğrafını gönderiniz." + ctx.message.author.mention)                
        notename = args[0]
        count = 2 
        string1 = ctx.message.content.split(' ', 2)[2]
        note = await aiofiles.open("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + notename, "w")
        await note.write(string1)
        await note.close()
        return await bot.send_message(ctx.message.channel, notename + " adlı notunuz kayıt edildi. " + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "Lütfen not adı ve içeriğini giriniz." + ctx.message.author.mention)
    return

@n.command(pass_context=True)
async def göster(ctx, *args):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    count = 0
    if not os.path.exists("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/"):
        return await bot.send_message(ctx.message.channel, "bu derse kayıtlı hiçbir notunuz yok." + ctx.message.author.mention)
    if len(args) == 1: #sonra çoklu not gösterme eklenecek.
        if os.path.isfile("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + args[0] ): 
            print("metin notu var")               
            notename = args[0]
            note = await aiofiles.open("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + notename, "r")
            notecontent = await note.read()
            await bot.send_message(ctx.message.channel, notecontent)
            count = 1

        if os.path.isfile("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + args[0] + ".jpg"):
            print("foto notuda var")
            count = 1
            await bot.send_file(ctx.message.channel, "db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + args[0] + ".jpg")
        else:
            if count == 0:
                await bot.send_message(ctx.message.channel, args[0] + " adında bir not bulunamadı. " + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "sadece bir argüman giriniz " + ctx.message.author.mention)
    return

@n.command(pass_context=True)
async def sil(ctx, *args):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    if not os.path.exists("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/"):
        os.makedirs("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/")
    if len(args) == 1: #sonra çoklu not ekleme eklenecek.
        if os.path.isfile("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + args[0]):
            os.remove("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/" + args[0])
            return await bot.send_message(ctx.message.channel, args[0] + " adındaki not silindi " + ctx.message.author.mention)
        else:
            return await bot.send_message(ctx.message.channel, args[0] + " adında bir not bulunamadı. " + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "sadece bir argüman giriniz " + ctx.message.author.mention)
    return

@n.command(pass_context=True)
async def liste(ctx, *args):
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
    dersargumani = cursor.fetchone()[0]
    if not os.path.exists("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/"):
        os.makedirs("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/")
    filelist = os.listdir("db/" + str(ctx.message.author) + "/Notlar/" + dersargumani + "/")
    filecount = len(filelist)
    i = 0
    string1 = '```\n'
    while i != filecount:
        string1 = string1 + filelist[i] + '\n'
        i = i + 1
    string1 = string1 + '```'
    return await bot.send_message(ctx.message.channel, string1)
    
@bot.command(pass_context=True)
async def hepsi(ctx, *args):
    if await sudo_check(ctx.message):
        i = 0
        global database
        cursor = database.cursor()
        user = f"'%{str(ctx.message.author)}%'"
        cursor.execute(f"SELECT ders FROM users WHERE username LIKE {user}")
        dersargumani = cursor.fetchone()[0]
        kacTane=len(os.listdir("db/" + str(ctx.message.author) + "/Çözülmemiş/" + dersargumani))
        while(i != kacTane-1):
            path = "db/" + str(ctx.message.author) + "/Çözülmemiş/" + dersargumani
            if os.path.exists(path):
                if os.path.isfile(path + "/" + dersargumani +str(i+1) + ".jpg"):
                    await bot.send_file(ctx.message.channel, path + "/" + dersargumani + str(i+1) + ".jpg")
                else:
                    await bot.send_message(ctx.message.channel, dersargumani + str(i+1) + " adında bir soru bulunamadı" + ctx.message.author.mention)

                if os.path.isfile("db/" + str(ctx.message.author) + "/Çözülmüş/" + dersargumani + "/" + dersargumani + str(i+1) + ".jpg"):
                    await bot.send_file(ctx.message.channel, "db/" + str(ctx.message.author) + "/Çözülmüş/" + dersargumani + "/" + dersargumani + str(i+1) + ".jpg")
                i = i + 1

            else:
                i = i + 1
                await bot.send_message(ctx.message.channel, dersargumani + " dersine kayıtlı hiçbir soru yok." + ctx.message.author.mention)
    else:
        return await bot.send_message(ctx.message.channel, "Bu komutu kullanmanız için gereken yetkilere sahip değilsiniz." + ctx.message.author.mention)

async def sudo_check(message: Message):
    
    global database
    cursor = database.cursor()
    user = f"'%{str(ctx.message.author)}%'"
    cursor.execute(f"SELECT sudo FROM users WHERE username LIKE {user}")
    sudo = cursor.fetchone()[0]
    if sudo == "1":
        print("Kullanıcı " + str(message.author) + " sudo yetkilerine sahip, izin verildi.")
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
async def yazi(ctx, *args):
    try:
        await bot.delete_message(ctx.message)
    except:
        print("bot mesaj düzenleme yetkisine sahip değil veya bu mesaj DM ile gönderildi.")
    count = 1 
    string1 = args[0]
    while (count != len(args)):
        string1 = string1 + " " + args[count]
        count = count + 1
    return await bot.send_message(ctx.message.channel, string1)

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