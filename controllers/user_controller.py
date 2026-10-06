async def register(data: dict):
    user = await prisma.user.create({ data })

    # Send welcome email
    await sendWelcomeEmail(user["email"])

    # Log the signup for analytics
    await prisma.usegeLog.create({
        data: { "userId": user["id"], "action": "signup", "tokens": 0, "costUsd": 0 }
    })

    # Notify admin on Slack
    await notifyAdminOnSlack(f"New signup: {user["email"]}")

    # Create default conversation
    await prisma.conversation.create({
        data: {
            "userId": user["id"],
            "title": "Welcome"
        }
    })