# 🔧 Instagram Monitor Bot - Troubleshooting Guide

## 🚨 Bot Notifications Not Showing

If your bot is not responding to commands or showing notifications, follow these steps:

### 1. **Test Bot Permissions**
Use the new `!test` command to check if the bot can send messages:
```
!test
```
This will test:
- ✅ Simple message sending
- ✅ Embed message sending  
- ✅ Message editing
- ✅ Adding reactions

### 2. **Debug Bot Configuration**
Use the `!debug` command to see detailed bot information:
```
!debug
```
This will show:
- 🤖 Bot information (name, ID, status)
- 🏠 Server and channel information
- 🔐 Bot permissions in the current channel
- ⚙️ Bot configuration

### 3. **Check Required Permissions**
Make sure your bot has these permissions in the channel:
- ✅ **Send Messages** - Required to send any messages
- ✅ **Embed Links** - Required to send rich embeds
- ✅ **Use External Emojis** - Required for custom emojis
- ✅ **Add Reactions** - Required for interactive reactions
- ✅ **Read Message History** - Required to read commands
- ✅ **View Channel** - Required to see the channel

### 4. **Common Issues & Solutions**

#### **Issue: Bot doesn't respond to any commands**
**Solution:**
1. Check if bot is online (green dot in Discord)
2. Verify bot token is correct
3. Check bot permissions in the channel
4. Make sure you're using the correct prefix (`!`)

#### **Issue: Bot responds but embeds don't show**
**Solution:**
1. Give bot "Embed Links" permission
2. Check if channel allows embeds
3. Try the `!test` command to verify embed functionality

#### **Issue: Bot shows error messages**
**Solution:**
1. Use `!debug` to see detailed error information
2. Check console output for error logs
3. Verify all required permissions are granted

### 5. **Bot Setup Checklist**

#### **Discord Bot Setup:**
- [ ] Bot token is valid and not expired
- [ ] Bot is added to your server
- [ ] Bot has proper permissions
- [ ] Message Content Intent is enabled

#### **Channel Permissions:**
- [ ] Bot can view the channel
- [ ] Bot can send messages
- [ ] Bot can embed links
- [ ] Bot can use external emojis
- [ ] Bot can add reactions

#### **User Permissions:**
- [ ] You have permission to use bot commands
- [ ] You're using the correct command prefix (`!`)
- [ ] Commands are typed correctly

### 6. **Testing Commands**

Try these commands in order:

1. **Basic connectivity:**
   ```
   !ping
   ```

2. **Permission test:**
   ```
   !test
   ```

3. **Debug information:**
   ```
   !debug
   ```

4. **Help and commands:**
   ```
   !help
   !commands
   ```

5. **Instagram monitoring:**
   ```
   !monitorban @instagram_username
   ```

### 7. **Console Output**

Check your console/terminal for these messages when starting the bot:
```
🚀 INSTAGRAM MONITOR BOT STARTED SUCCESSFULLY!
🤖 Bot Name: [Your Bot Name]
🆔 Bot ID: [Bot ID]
🏠 Servers: [Number of servers]
⚡ Latency: [Latency in ms]
```

### 8. **Still Having Issues?**

If the bot still doesn't work after following these steps:

1. **Check the console** for error messages
2. **Verify your bot token** is correct
3. **Re-add the bot** to your server with proper permissions
4. **Contact support** with the error messages from console

### 9. **Quick Fix Commands**

If you need to quickly test if the bot is working:

```bash
# Test basic functionality
!ping

# Test permissions and embeds
!test

# Get detailed debug info
!debug

# See all available commands
!commands
```

---

## 🎯 **Success Indicators**

When the bot is working correctly, you should see:
- ✅ Bot responds to `!ping` with latency information
- ✅ Bot sends rich embeds with colors and formatting
- ✅ Bot can edit messages and add reactions
- ✅ Bot shows detailed Instagram data when monitoring accounts
- ✅ No error messages in console or Discord

If you see these indicators, your bot is working perfectly! 🎉 