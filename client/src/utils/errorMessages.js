export const ERROR_MESSAGES = {
  SERVER_LOADING: `🤖 **Oops! Backend Server is Having a Moment** 

Hey there, fellow developer! 👋 

If you just started the backend server, expecially the **first time**, don't panic! The server is probably still:
- ☕ Waking up from its digital slumber
- 🧠 Loading that chunky LLM model (this is the slow part!)
- 🔧 Getting all its AI neurons in order

**⏰ Expected Wait Time:** 5-10 minutes (perfect time for a coffee break!)

**🕵️ How to Check Progress:**
Run this command in your terminal:
\`\`\`bash
docker compose logs server
\`\`\`

**✅ Look for this magic message:**
\`INFO - Chat model and processor loaded successfully\`

Once you see that, just **refresh this page** and you're good to go! 

**🎉 Pro Tip:** The server only needs this long setup on the first boot. Subsequent restarts are much faster!

*Meanwhile, why not grab a snack? The AI is doing some heavy lifting! 💪*`,

  WELCOME: "Hello! Welcome to the chat app. Start a new conversation!",
};
