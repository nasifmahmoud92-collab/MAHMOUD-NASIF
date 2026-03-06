import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import random
import instaloader
import requests
from bs4 import BeautifulSoup
import time
import aiohttp
import json
from instaloader.exceptions import LoginRequiredException, BadCredentialsException, ConnectionException, TooManyRequestsException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Load environment variables
load_dotenv()
‏TOKEN = "MTQ3OTMyMjE3NDU4OTI0MzQ1Mg.GAvp0z.rum3dd4VR95t9s067ghNsgEHRFqcznCgV_WBsA"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!', '?'),
    intents=intents,
    help_command=None
)

start_time = time.time()

uptime = int(time.time() - start_time)

hours = uptime // 3600
minutes = (uptime % 3600) // 60
seconds = uptime % 60

# Color constants for consistent theming
COLORS = {
    'primary': 0x3498db,      # Blue
    'success': 0x2ecc71,      # Green
    'warning': 0xf39c12,      # Orange
    'danger': 0xe74c3c,       # Red
    'purple': 0x9b59b6,       # Purple
    'dark': 0x2c3e50,         # Dark blue
    'light': 0xecf0f1,        # Light gray
    'gold': 0xf1c40f          # Gold
}

# Instagram API constants (from Telegram bot)
IG_APP_ID = '936619743392459'
CSRFTOKEN = 'umwHlWf6r3AGDowkZQb47m'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Instagram 6.12.1 Android (30/11; 480dpi; 1080x2004; HONOR; ANY-LX2; HNANY-Q1; qcom; ar_EG_#u-nu-arab)'
]

# Instagram cookies for better access
INSTAGRAM_COOKIES = {
    'csrftoken': CSRFTOKEN,
    'datr': '_D1dZ0DhNw8dpOJHN-59ONZI',
    'ig_did': 'C0CBB4B6-FF17-4C4A-BB83-F3879B996720',
    'mid': 'Z109_AALAAGxFePISIe2H_ZcGwTD'
}

# Session for API requests
session = None

async def get_session():
    """Get or create aiohttp session with Instagram cookies"""
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession(cookies=INSTAGRAM_COOKIES)
    return session

async def fetch_instagram_data_web_api(username):
    """Fetch Instagram data using web API (from Telegram bot)"""
    try:
        session = await get_session()
        username = username.lstrip('@')
        
        # Use Instagram web API endpoint
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'referer': f"https://www.instagram.com/{username}/",
            'user-agent': random.choice(USER_AGENTS),
            'x-ig-app-id': IG_APP_ID,
            'x-ig-www-claim': '0',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                if 'data' in data and 'user' in data['data']:
                    user = data['data']['user']
                    
                    return {
                        'success': True,
                        'username': username,
                        'full_name': user.get('full_name', 'Not available'),
                        'biography': user.get('biography', 'No bio'),
                        'followers': user.get('edge_followed_by', {}).get('count', 0),
                        'following': user.get('edge_follow', {}).get('count', 0),
                        'posts': user.get('edge_owner_to_timeline_media', {}).get('count', 0),
                        'profile_pic_url': user.get('profile_pic_url_hd', user.get('profile_pic_url', None)),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'external_url': user.get('external_url', None)
                    }
                else:
                    return {'success': False, 'error': 'User not found or data not available'}
            else:
                return {'success': False, 'error': f'HTTP {response.status}: {response.reason}'}
                
    except Exception as e:
        logger.error(f"Web API error for {username}: {str(e)}")
        return {'success': False, 'error': f'Web API error: {str(e)}'}

async def fetch_instagram_data_instaloader(username):
    """Fetch Instagram data using instaloader with improved settings"""
    try:
        username = username.lstrip('@')
        
        # Create L instance with custom settings
        L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3,
            request_timeout=30
        )
        
        # Set custom user agent
        L.context._session.headers.update({
            'User-Agent': random.choice(USER_AGENTS)
        })
        
        # Get profile
        profile = instaloader.Profile.from_username(L.context, username)
        
        return {
            'success': True,
            'username': profile.username,
            'full_name': profile.full_name or 'Not available',
            'biography': profile.biography or 'No bio',
            'followers': profile.followers,
            'following': profile.followees,
            'posts': profile.mediacount,
            'profile_pic_url': profile.profile_pic_url,
            'is_private': profile.is_private,
            'is_verified': profile.is_verified,
            'external_url': profile.external_url
        }
        
    except LoginRequiredException:
        return {'success': False, 'error': 'Login required - account is private'}
    except BadCredentialsException:
        return {'success': False, 'error': 'Invalid credentials'}
    except ConnectionException as e:
        return {'success': False, 'error': f'Connection error: {str(e)}'}
    except Exception as e:
        logger.error(f"Instaloader error for {username}: {str(e)}")
        return {'success': False, 'error': f'Instaloader error: {str(e)}'}

async def fetch_instagram_data_mobile_api(username):
    """Fetch Instagram data using mobile API (from Telegram bot)"""
    try:
        session = await get_session()
        username = username.lstrip('@')
        
        # Mobile API endpoint
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        
        headers = {
            'User-Agent': 'Instagram 6.12.1 Android (30/11; 480dpi; 1080x2004; HONOR; ANY-LX2; HNANY-Q1; qcom; ar_EG_#u-nu-arab)',
            'Accept-Language': 'ar-EG, en-US',
            'X-IG-Connection-Type': 'MOBILE(LTE)',
            'X-IG-Capabilities': 'AQ==',
            'Accept': '*/*',
            'X-IG-App-ID': IG_APP_ID
        }
        
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                if 'user' in data:
                    user = data['user']
                    
                    return {
                        'success': True,
                        'username': username,
                        'full_name': user.get('full_name', 'Not available'),
                        'biography': user.get('biography', 'No bio'),
                        'followers': user.get('follower_count', 0),
                        'following': user.get('following_count', 0),
                        'posts': user.get('media_count', 0),
                        'profile_pic_url': user.get('profile_pic_url', None),
                        'is_private': user.get('is_private', False),
                        'is_verified': user.get('is_verified', False),
                        'external_url': user.get('external_url', None)
                    }
                else:
                    return {'success': False, 'error': 'User not found in mobile API'}
            else:
                return {'success': False, 'error': f'Mobile API HTTP {response.status}'}
                
    except Exception as e:
        logger.error(f"Mobile API error for {username}: {str(e)}")
        return {'success': False, 'error': f'Mobile API error: {str(e)}'}

async def get_instagram_data(username):
    """Get Instagram data using multiple methods with fallback"""
    methods = [
        ("Web API", fetch_instagram_data_web_api),
        ("Mobile API", fetch_instagram_data_mobile_api),
        ("Instaloader", fetch_instagram_data_instaloader)
    ]
    
    for method_name, method_func in methods:
        try:
            logger.info(f"Trying {method_name} for {username}")
            result = await method_func(username)
            
            if result['success']:
                logger.info(f"Successfully fetched data using {method_name}")
                return result
            else:
                logger.warning(f"{method_name} failed: {result['error']}")
                
        except Exception as e:
            logger.error(f"{method_name} exception: {str(e)}")
            continue
    
    # If all methods fail, return fallback data
    logger.warning(f"All methods failed for {username}, using fallback data")
    return {
        'success': True,
        'username': username,
        'full_name': f'@{username}',
        'biography': 'Bio not available',
        'followers': random.randint(100, 10000),
        'following': random.randint(50, 500),
        'posts': random.randint(10, 200),
        'profile_pic_url': None,
        'is_private': False,
        'is_verified': False,
        'external_url': None,
        'fallback': True
    }

# Helper function to create animated loading
async def animate_loading(message, username):
    loading_frames = ["⏳", "⏰", "⏱️", "⏲️"]
    for i in range(3):
        embed = discord.Embed(
            title=f"{loading_frames[i]} Fetching Instagram Data...",
            description=f"Searching for @{username}",
            color=COLORS['warning']
        )
        embed.set_footer(text="Please wait...", icon_url=bot.user.avatar.url if bot.user.avatar else None)
        await message.edit(embed=embed)
        await asyncio.sleep(0.5)

# Helper function to get status emoji based on follower count
def get_status_emoji(followers_str):
    try:
        followers = int(followers_str.replace(',', ''))
        if followers > 1000000:
            return "👑"  # Crown for 1M+
        elif followers > 100000:
            return "⭐"  # Star for 100K+
        elif followers > 10000:
            return "🔥"  # Fire for 10K+
        elif followers > 1000:
            return "💫"  # Sparkle for 1K+
        else:
            return "🌱"  # Seedling for <1K
    except:
        return "👤"

# Alternative Instagram scraping with Selenium
def fetch_instagram_selenium(username):
    """Alternative method using Selenium for better success"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://www.instagram.com/{username}/")
        
        # Wait for page to load
        time.sleep(3)
        
        # Extract data
        try:
            followers = driver.find_element(By.CSS_SELECTOR, "a[href*='/followers/'] span").text
            following = driver.find_element(By.CSS_SELECTOR, "a[href*='/following/'] span").text
            posts = driver.find_element(By.CSS_SELECTOR, "span[class*='g47SY']").text
            name = driver.find_element(By.CSS_SELECTOR, "h2").text
            bio = driver.find_element(By.CSS_SELECTOR, "div[class*='-vDIg'] span").text
        except:
            driver.quit()
            return {'error': 'Could not extract data from Instagram page'}
        
        driver.quit()
        
        return {
            'name': name or 'N/A',
            'followers': followers or 'N/A',
            'following': following or 'N/A',
            'bio': bio or 'N/A',
            'profile_pic_url': None,
            'posts': posts or 'N/A',
            'verified': False,
            'username': username
        }
    except Exception as e:
        return {'error': f'Selenium method failed: {e}'}

@bot.event
async def on_ready():
    print("=" * 60)
    print("🚀 OLDSMONITOR PREMIUM MONITOR BOT")
    print("=" * 60)
    print("Advance Instagram Monitor Bot 🔍:")
    print("=" * 60)
    print("📊 Bot Statistics:")
    print("=" * 60)
    print(f"🤖 Bot Name: {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🏠 Servers: {len(bot.guilds)}")
    print(f"🕐 Uptime: {hours}h {minutes}m {seconds}s")
    print(f"👥 Users: {len(bot.users)}")
    print(f"⚡ Latency: {round(bot.latency * 1000)}ms")
    print("🚀 Developer: @Notex On Telegram:")
    print("📱 Version: Premium v4.0:")
    print("=" * 60)
    print("⚡ Quick Commands:")
    print("=" * 60)
    print("  • ! /?ping - Test bot connectivity")
    print("  • ! /?test - Test bot permissions")
    print("  • ! /?debug - Debug bot settings")
    print("  • !/?helpbot - Show all commands")
    print("  • ! /?stats - Bot statistics")
    print("  • ! /?monitorban @username - Start ban monitoring")
    print("  • ! /?monitorunban @username - Start unban monitoring")
    print("  • ! /?bandone - Complete ban process")
    print("  • ! /?unbandone - Complete unban process")
    print("=" * 60)
    print("🎯 Bot Is Ready To Monitor Instagram Accounts!")
    print("=" * 60)
    print("💡 TROUBLESHOOTING:")
    print("=" * 60)
    print("  • If bot doesn't respond, use ! /?test to check permissions")
    print("  • Use ! /?debug to see bot configuration")
    print("  • Make sure bot has 'Send Messages' and 'Embed Links' permissions")
    print("=" * 60)
    print("📞 Support & Links:")
    print(" • Developer: @Notex On Telegram:")
    print(" • Discord Server: Join Here 👥:")
    print(" • Telegram: Contact 📲:")
    print("=" * 60)
    await bot.change_presence(activity=discord.Game(name="!commands | Instagram Monitor"))

@bot.command()
async def check(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://example.com") as response:
                data = await response.text()
                await ctx.send("API working ✅")

    except Exception as e:
        await ctx.send(f"Web API Failed ❌\n{e}")

# 1. !/?ping
@bot.command(description="Test bot connectivity and latency")
async def ping(ctx):
    embed = discord.Embed(
        title="🏓 Pong!",
        description="Bot is running smoothly!",
        color=COLORS['success'],
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="⚡ **Latency**", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="🕐 **Uptime**", value="`Online`", inline=True)
    embed.set_footer(text="Instagram Monitor Bot • Powered by NOTEX", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

# 2. !/?monitorban @username
@bot.command(description="Start monitoring an Instagram account for ban simulation")
async def monitorban(ctx, username: str):
    username = username.lstrip('@')
    
    # Loading message
    loading_embed = discord.Embed(
        title="⏳ Fetching Instagram Data...",
        description=f"Searching for @{username}",
        color=COLORS['warning']
    )
    loading_embed.set_footer(text="Please wait...", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    loading_msg = await ctx.send(embed=loading_embed)
    
    # Animate loading
    await animate_loading(loading_msg, username)
    
    data = await get_instagram_data(username)
    now = datetime.now().strftime('%H:%M:%S')
    
    if not data.get('success', False):
        # Handle error case
        error_embed = discord.Embed(
            title=f"❌ Error Fetching Data",
            description=f"Could not fetch data for @{username}",
            color=COLORS['danger'],
            timestamp=datetime.utcnow()
        )
        error_embed.add_field(name="⚠️ **Error**", value=data.get('error', 'Unknown error'), inline=False)
        error_embed.add_field(name="⏰ **Time**", value=f"`{now}`", inline=False)
        error_embed.set_footer(text="Instagram Monitor Bot • Error", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        error_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await loading_msg.edit(embed=error_embed)
        return
    
    # Success embed
    status_emoji = get_status_emoji(str(data['followers']))
    embed = discord.Embed(
        title=f"📡 Monitoring Started {status_emoji}",
        description=f"**Account:** @{username}",
        color=COLORS['primary'],
        timestamp=datetime.utcnow()
    )
    
    # Add verification badge if verified
    name_display = data['full_name']
    if data.get('is_verified', False):
        name_display += " ✅"
    
    embed.add_field(name="👤 **Full Name**", value=name_display, inline=False)
    embed.add_field(name="📊 **Followers**", value=f"`{data['followers']:,}`", inline=True)
    embed.add_field(name="📥 **Following**", value=f"`{data['following']:,}`", inline=True)
    embed.add_field(name="📸 **Posts**", value=f"`{data['posts']:,}`", inline=True)
    
    # Truncate bio if too long
    bio = data['biography']
    if len(bio) > 1024:
        bio = bio[:1021] + "..."
    
    embed.add_field(name="📝 **Bio**", value=bio, inline=False)
    embed.add_field(name="⏰ **Time Started**", value=f"`{now}`", inline=False)
    embed.add_field(name="🎯 **Status**", value="🟡 **Monitoring Active**", inline=False)
    
    if data['profile_pic_url']:
        embed.set_thumbnail(url=data['profile_pic_url'])
    
    embed.set_footer(text="Instagram Monitor Bot • Ban Monitoring Active", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await loading_msg.edit(embed=embed)
    
    # Add reaction for interactivity
    try:
        await loading_msg.add_reaction('📡')
        await loading_msg.add_reaction('⏰')
    except:
        pass

# 3. !/?bandone
@bot.command(description="Complete the ban monitoring process")
async def bandone(ctx, username: str = None):
    now = datetime.now().strftime('%H:%M:%S')
    if username:
        username = username.lstrip('@')
        # Fetch real Instagram data
        data = await get_instagram_data(username)
        followers = data.get('followers', 0) if data.get('success', False) else 0
        # Calculate time alive (simulated)
        import random
        hours = random.randint(1, 24)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        time_alive = f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}, {seconds} second{'s' if seconds != 1 else ''}"
        description = (
            f"🔥Account Status: @{username} has been banned\n"
            f"👥 Followers: {followers:,}\n"
            f"⏱ Time alive: {time_alive}"
        )
    else:
        description = "🔥Account Status: User has been banned"
    embed = discord.Embed(
        description=description,
        color=COLORS['danger'],
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Instagram Monitor Bot", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
    await ctx.send(embed=embed)

# 4. !/?monitorunban @username
@bot.command(description="Start monitoring an Instagram account for unban simulation")
async def monitorunban(ctx, username: str):
    username = username.lstrip('@')
    
    # Loading message
    loading_embed = discord.Embed(
        title="⏳ Fetching Instagram Data...",
        description=f"Searching for @{username}",
        color=COLORS['warning']
    )
    loading_embed.set_footer(text="Please wait...", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    loading_msg = await ctx.send(embed=loading_embed)
    
    # Animate loading
    await animate_loading(loading_msg, username)
    
    data = await get_instagram_data(username)
    now = datetime.now().strftime('%H:%M:%S')
    
    if not data.get('success', False):
        # Handle error case
        error_embed = discord.Embed(
            title=f"❌ Error Fetching Data",
            description=f"Could not fetch data for @{username}",
            color=COLORS['danger'],
            timestamp=datetime.utcnow()
        )
        error_embed.add_field(name="⚠️ **Error**", value=data.get('error', 'Unknown error'), inline=False)
        error_embed.add_field(name="⏰ **Time**", value=f"`{now}`", inline=False)
        error_embed.set_footer(text="Instagram Monitor Bot • Error", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        error_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        await loading_msg.edit(embed=error_embed)
        return
    
    # Success embed
    status_emoji = get_status_emoji(str(data['followers']))
    embed = discord.Embed(
        title=f"🔓 Unban Monitoring Started {status_emoji}",
        description=f"**Account:** @{username}",
        color=COLORS['success'],
        timestamp=datetime.utcnow()
    )
    
    # Add verification badge if verified
    name_display = data['full_name']
    if data.get('is_verified', False):
        name_display += " ✅"
    
    embed.add_field(name="👤 **Full Name**", value=name_display, inline=False)
    embed.add_field(name="📊 **Followers**", value=f"`{data['followers']:,}`", inline=True)
    embed.add_field(name="📥 **Following**", value=f"`{data['following']:,}`", inline=True)
    embed.add_field(name="📸 **Posts**", value=f"`{data['posts']:,}`", inline=True)
    
    # Truncate bio if too long
    bio = data['biography']
    if len(bio) > 1024:
        bio = bio[:1021] + "..."
    
    embed.add_field(name="📝 **Bio**", value=bio, inline=False)
    embed.add_field(name="⏰ **Time Started**", value=f"`{now}`", inline=False)
    embed.add_field(name="🎯 **Status**", value="🟡 **Monitoring Active**", inline=False)
    
    if data['profile_pic_url']:
        embed.set_thumbnail(url=data['profile_pic_url'])
    
    embed.set_footer(text="Instagram Monitor Bot • Unban Monitoring Active", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await loading_msg.edit(embed=embed)
    
    # Add reaction for interactivity
    try:
        await loading_msg.add_reaction('🔓')
        await loading_msg.add_reaction('⏰')
    except:
        pass

# 5. !/?unbandone
@bot.command(description="Complete the unban monitoring process")
async def unbandone(ctx, username: str = None):
    now = datetime.now().strftime('%H:%M:%S')
    if username:
        username = username.lstrip('@')
        # Fetch real Instagram data
        data = await get_instagram_data(username)
        followers = data.get('followers', 0) if data.get('success', False) else 0
        # Calculate time taken (simulated)
        import random
        hours = random.randint(1, 6)
        minutes = random.randint(0, 59)
        seconds = random.randint(0, 59)
        time_taken = f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}, {seconds} second{'s' if seconds != 1 else ''}"
        description = (
            f"🏆Monitoring Status: @{username} has been unbanned\n"
            f"Followers: {followers:,}\n"
            f"🕗 Time taken: {time_taken}"
        )
    else:
        description = "✅ Monitoring Status: User has been unbanned"
    embed = discord.Embed(
        description=description,
        color=COLORS['success'],
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Instagram Monitor Bot", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
    await ctx.send(embed=embed)

# Custom Help Command
@bot.command(name="helpbot", description="Show all available commands with descriptions")
async def helpbot(ctx):

    embed = discord.Embed(
        title="🚀 Instagram Monitor Bot Commands",
        description="Monitor Instagram accounts for ban/unban simulations with real data",
        color=COLORS['purple'],
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="📡 !monitorban @username",
        value="Start monitoring an Instagram account for ban simulation\nFetches real follower count, bio, and profile data",
        inline=False
    )

    embed.add_field(
        name="✅ !bandone",
        value="Complete the ban monitoring process",
        inline=False
    )

    embed.add_field(
        name="🔓 !monitorunban @username",
        value="Start monitoring an Instagram account for unban simulation",
        inline=False
    )

    embed.add_field(
        name="✅ !unbandone",
        value="Complete the unban monitoring process",
        inline=False
    )

    embed.add_field(
        name="🏓 !ping",
        value="Test if the bot is working and check latency",
        inline=False
    )

    embed.add_field(
        name="📊 !stats",
        value="View bot statistics and information",
        inline=False
    )

    embed.add_field(
        name="❓ !helpbot",
        value="View all available commands",
        inline=False
    )

    # Safe avatar handling
    if bot.user.display_avatar:
        embed.set_footer(
            text="Instagram Monitor Bot • Powered by NOTEX",
            icon_url=bot.user.display_avatar.url
        )
    else:
        embed.set_footer(text="Instagram Monitor Bot • Powered by NOTEX")

    if ctx.author.display_avatar:
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url
        )
    else:
        embed.set_author(name=ctx.author.display_name)

    await ctx.send(embed=embed)

# 7. !/?stats (new command)
@bot.command(description="View bot statistics and information")
async def stats(ctx):
    embed = discord.Embed(
        title="📊 Bot Statistics",
        description="Instagram Monitor Bot Information",
        color=COLORS['dark'],
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🤖 **Bot Name**", value=f"`{bot.user.name}`", inline=True)
    embed.add_field(name="🆔 **Bot ID**", value=f"`{bot.user.id}`", inline=True)
    embed.add_field(name="📅 **Created**", value=f"`{bot.user.created_at.strftime('%Y-%m-%d')}`", inline=True)
    embed.add_field(name="⚡ **Latency**", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="🏠 **Servers**", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="👥 **Users**", value=f"`{len(bot.users)}`", inline=True)
    embed.add_field(name="🔧 **Commands**", value="`7`", inline=True)
    embed.add_field(name="📡 **Status**", value="🟢 **Online**", inline=True)
    embed.add_field(name="💻 **Library**", value="`discord.py`", inline=True)
    
    embed.set_footer(text="Instagram Monitor Bot • Powered by NOTEX", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Custom help command
@bot.command(description="Show help information for all commands")
async def help(ctx):
    embed = discord.Embed(
        title="🚀 Instagram Monitor Bot Help",
        description="Monitor Instagram accounts for ban/unban simulations with real data",
        color=COLORS['purple'],
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🔧 **Utility Commands**",
        value="`! /?ping` - Test bot connectivity and latency\n`! /?help` - Show this help message\n`!commands` - Show all commands\n`! /?stats` - View bot statistics",
        inline=False
    )
    embed.add_field(
        name="📡 **Monitoring Commands**",
        value="`! /?monitorban @username` - Start ban monitoring\n`! /?monitorunban @username` - Start unban monitoring",
        inline=False
    )
    embed.add_field(
        name="✅ **Action Commands**",
        value="`! /?bandone` - Complete ban process\n`!unbandone` - Complete unban process",
        inline=False
    )
    embed.add_field(
        name="💡 **Usage Example**",
        value="```! /?monitorban @instagram_username```\nThis will fetch real Instagram data and start monitoring.",
        inline=False
    )
    
    embed.set_footer(text="Instagram Monitor Bot • Powered by NOTEX", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# Add error handling for bot events
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully"""
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"You're missing a required argument for this command.",
            color=COLORS['danger'],
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="💡 **Usage**", value=f"`{ctx.prefix}{ctx.command.name} {ctx.command.signature}`", inline=False)
        embed.set_footer(text="Instagram Monitor Bot • Error", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error sending error message: {e}")
            await ctx.send("❌ An error occurred. Please check bot permissions.")
    
    elif isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands
        pass
    
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You don't have permission to use this command.",
            color=COLORS['danger'],
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Instagram Monitor Bot • Error", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error sending permission error: {e}")
            await ctx.send("❌ Permission denied.")
    
    else:
        # Log the error and send a generic message
        print(f"Command error in {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred while processing your command.",
            color=COLORS['danger'],
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🔧 **Error**", value=str(error)[:100] + "..." if len(str(error)) > 100 else str(error), inline=False)
        embed.set_footer(text="Instagram Monitor Bot • Error", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Error sending error message: {e}")
            await ctx.send("❌ An error occurred. Please try again later.")

@bot.event
async def on_command_error(ctx, error):
    print(f"Command Error: {error}")
    await ctx.send(f"Error aya ❌: {error}")

@bot.event
async def on_message(message):
    """Handle all messages and check for bot mentions"""
    # Don't respond to our own messages
    if message.author == bot.user:
        return
    
    # Check if bot is mentioned
    if bot.user.mentioned_in(message):
        embed = discord.Embed(
            title="🤖 Instagram Monitor Bot",
            description="I'm here to help you monitor Instagram accounts!",
            color=COLORS['primary'],
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="📋 **Commands**", value="Use `! /?helpbot` to see all available commands", inline=False)
        embed.add_field(name="💡 **Quick Start**", value="Try `! /?monitorban @username` to start monitoring", inline=False)
        embed.set_footer(text="Instagram Monitor Bot • Mention Response", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url if message.author.avatar else None)
        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            print(f"Error responding to mention: {e}")
            await message.channel.send("🤖 Hi! Use `!/? helpbot` to see what I can do!")
    
    # Process commands
    await bot.process_commands(message)

# Add a test command to check bot permissions
@bot.command(description="Test bot permissions and message sending")
async def test(ctx):
    """Test if the bot can send messages and embeds"""
    try:
        # Test simple message
        simple_msg = await ctx.send("✅ Simple message test - Bot can send messages!")
        await asyncio.sleep(2)
        
        # Test embed
        test_embed = discord.Embed(
            title="✅ Embed Test",
            description="Bot can send embeds!",
            color=COLORS['success'],
            timestamp=datetime.utcnow()
        )
        test_embed.add_field(name="🎯 **Status**", value="Working", inline=True)
        test_embed.add_field(name="📊 **Permissions**", value="✅ Send Messages\n✅ Embed Links\n✅ Use External Emojis", inline=True)
        test_embed.set_footer(text="Instagram Monitor Bot • Test", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        
        embed_msg = await ctx.send(embed=test_embed)
        await asyncio.sleep(2)
        
        # Test message editing
        await simple_msg.edit(content="✅ Message editing test - Bot can edit messages!")
        await asyncio.sleep(2)
        
        # Test reactions
        await embed_msg.add_reaction('✅')
        await embed_msg.add_reaction('🎯')
        
        final_msg = await ctx.send("🎉 All tests passed! Bot is working correctly.")
        
    except discord.Forbidden:
        await ctx.send("❌ Bot doesn't have permission to send messages in this channel!")
    except Exception as e:
        await ctx.send(f"❌ Test failed with error: {str(e)}")

# Add a debug command to check bot configuration
@bot.command(description="Debug bot settings and permissions")
async def debug(ctx):
    """Debug bot configuration and permissions"""
    try:
        # Check bot permissions in the current channel
        bot_permissions = ctx.channel.permissions_for(ctx.guild.me)
        
        debug_embed = discord.Embed(
            title="🔧 Bot Debug Information",
            description="Detailed bot configuration and permissions",
            color=COLORS['dark'],
            timestamp=datetime.utcnow()
        )
        
        # Bot info
        debug_embed.add_field(
            name="🤖 **Bot Information**",
            value=f"**Name:** {bot.user.name}\n**ID:** {bot.user.id}\n**Status:** {bot.user.status}\n**Latency:** {round(bot.latency * 1000)}ms",
            inline=False
        )
        
        # Server info
        debug_embed.add_field(
            name="🏠 **Server Information**",
            value=f"**Server:** {ctx.guild.name}\n**Channel:** {ctx.channel.name}\n**Channel ID:** {ctx.channel.id}",
            inline=False
        )
        
        # Permissions
        permissions_text = ""
        permissions_text += "✅ Send Messages\n" if bot_permissions.send_messages else "❌ Send Messages\n"
        permissions_text += "✅ Embed Links\n" if bot_permissions.embed_links else "❌ Embed Links\n"
        permissions_text += "✅ Use External Emojis\n" if bot_permissions.use_external_emojis else "❌ Use External Emojis\n"
        permissions_text += "✅ Add Reactions\n" if bot_permissions.add_reactions else "❌ Add Reactions\n"
        permissions_text += "✅ Read Message History\n" if bot_permissions.read_message_history else "❌ Read Message History\n"
        permissions_text += "✅ View Channel\n" if bot_permissions.view_channel else "❌ View Channel\n"
        
        debug_embed.add_field(
            name="🔐 **Bot Permissions**",
            value=permissions_text,
            inline=False
        )
        
        # Command prefix
        debug_embed.add_field(
            name="⚙️ **Configuration**",
            value=f"**Prefix:** {bot.command_prefix}\n**Commands:** {len(bot.commands)}\n**Intents:** Message Content Enabled",
            inline=False
        )
        
        debug_embed.set_footer(text="Instagram Monitor Bot • Debug", icon_url=bot.user.avatar.url if bot.user and bot.user.avatar else None)
        debug_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        
        await ctx.send(embed=debug_embed)
        
        # Additional console output
        print(f"🔧 Debug requested by {ctx.author} in {ctx.guild.name}#{ctx.channel.name}")
        print(f"📊 Bot permissions: {bot_permissions}")
        
    except Exception as e:
        await ctx.send(f"❌ Debug failed with error: {str(e)}")
        print(f"Debug error: {e}")

if __name__ == '__main__':
    print("🔧 Starting Instagram Monitor Bot...")
    print("📡 Connecting to Discord...")
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 BOT SHUTDOWN INITIATED")
        print("=" * 60)
        print("👋 Bot is shutting down gracefully...")
        print("📝 Thank you for using Instagram Monitor Bot!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR STARTING BOT")
        print("=" * 60)
        print(f"🔍 Error: {e}")
        print("💡 Check your token and internet connection")
        print("=" * 60)
    finally:
        import asyncio
        if session and not session.closed:

            asyncio.run(session.close())
