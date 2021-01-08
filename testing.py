
import discord
import smtplib, ssl
import dotenv
from random import randint
import time

client = discord.Client()

load_dotenv()
DISCORD_TOKEN=os.getenv("DAANISH_TOKEN")


def send_email(user_email, randomint):
    gmail_user = "brown25devteam@gmail.com"
    gmail_password = "BrunoIsCool"

    sent_from = gmail_user
    to = ['']
    to.insert(0, user_email)

    subject = 'Your Verification Code'
    body = str(randomint)

    email_text = "Subject: Verification Code: " + body

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print("EMAIL SENT")

@client.event
async def on_ready():
    print('poggers')


@client.event
async def on_message(message):
    channel = message.channel
    mainchannel = client.get_channel(797146853309153353)
    if channel.name == "dev" and message.content.startswith("!start"):
        await mainchannel.send("Welcome! In order to gain access to the Brown Class of 2025 Discord server, we ask that you complete a verification with your Brown email address. To begin the process, react to this message with the check mark.")
    if message.content.startswith("Welcome! In order to gain access to the Brown Class of 2025 Discord server, we ask that you complete a verification with your Brown email address. To begin the process, react to this message with the check mark."):
        await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
#    user = await client.fetch_user(message.author.id)
#    mainchannel = client.get_channel(797146853309153353)
#    if channel.name == "dev" and message.content.startswith("!start"):
#        await mainchannel.send("Type !dm to...")
#    if message.content.startswith("!dm") and channel.name == "roles-assign":
#        await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
#        await user.send("this should be a dm")
#        email = await client.wait_for('message')
#        send_email(email.content)


@client.event
async def on_reaction_add(reaction, user):
    userdm = await client.fetch_user(user.id)
    if reaction.message.content.startswith("Welcome! In order to gain access to the Brown Class of 2025 Discord server, we ask that you complete a verification with your Brown email address. To begin the process, react to this message with the check mark.") and reaction.emoji == '\N{WHITE HEAVY CHECK MARK}':
        await userdm.send("To confirm you are a brown student, please send your email in the format *email@brown.edu*")
        email = await client.wait_for('message')
        if email.content.find('brown.edu') < 1:
            await userdm.send("Sorry, the email you sent was not a Brown email. Please try the process all over again. To do this, un-react to the main message and react again.")
        else:
            randominteger = randint(100000, 999999)
            print("RANDOM INT IS: " + str(randominteger))
            send_email(email.content, randominteger)
            await userdm.send("an email has been sent to " + email.content + ". What is your verification code?")
            time.sleep(0.25)
            code = await client.wait_for('message')
            print("THE CODE IS: " + code.content)
            role = discord.utils.get(user.guild.roles, name='TestRole')
            if code.content == str(randominteger):
                print("YAY IT WORKED")
                await userdm.send("awesome, the codes matched, welcome to the Brown University Class of 2025 Server!")
                await user.add_roles(role)

client.run(DAANISH_TOKEN)
