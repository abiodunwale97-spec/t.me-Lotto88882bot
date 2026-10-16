"""
MentalModelsDaily_bot — Telegram Bot
Sends one mental model on request, or one per day by subscription.

Run locally:
    export BOT_TOKEN="your-token-from-botfather"
    python bot.py

On Railway, set BOT_TOKEN in the Variables tab. Never hard-code it here.
"""

import json
import logging
import os
import random
from datetime import time as dtime

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SUBSCRIBERS_FILE = "subscribers.json"

# ---------------------------------------------------------------------------
# CONTENT LIBRARY — add new entries any time, nothing else needs to change
# ---------------------------------------------------------------------------

MODELS = [
    {
        "title": "First Principles Thinking",
        "body": (
            "Break a problem down to the basic facts you know are true, then build "
            "your reasoning upward from there.\n\n"
            "Instead of copying what others do with small tweaks, ask: what is "
            "actually true here?"
        ),
    },
    {
        "title": "The Pareto Principle (80/20)",
        "body": (
            "Roughly 80% of results come from 20% of the causes.\n\n"
            "Find the few inputs that matter most and give them the most attention."
        ),
    },
    {
        "title": "Occam's Razor",
        "body": (
            "When several explanations fit the facts, the one needing the fewest "
            "assumptions is usually the best place to start.\n\n"
            "Check the simple causes before building a complicated theory."
        ),
    },
    {
        "title": "Inversion",
        "body": (
            "Instead of asking how to succeed, ask what would guarantee failure, "
            "then avoid it.\n\n"
            "Many problems become clearer when you work backwards."
        ),
    },
    {
        "title": "Second-Order Thinking",
        "body": (
            "First-order thinking asks what happens next. Second-order thinking "
            "asks: and then what?\n\n"
            "Follow a decision's consequences a few steps ahead before you commit."
        ),
    },
    {
        "title": "Compounding",
        "body": (
            "Small gains that build on each other grow far faster than they look at "
            "the start.\n\n"
            "Consistency over a long time usually beats a single big push."
        ),
    },
    {
        "title": "Circle of Competence",
        "body": (
            "Know the areas you understand well, and be honest about where your "
            "knowledge ends.\n\n"
            "Outside that circle, learn first or ask someone who knows."
        ),
    },
    {
        "title": "The Map Is Not the Territory",
        "body": (
            "Every model, plan or description simplifies reality.\n\n"
            "When reality disagrees with your map, trust reality and update the map."
        ),
    },
    {
        "title": "Opportunity Cost",
        "body": (
            "The real cost of a choice is the best alternative you give up.\n\n"
            "Before saying yes, ask what you are saying no to."
        ),
    },
    {
        "title": "Confirmation Bias",
        "body": (
            "We tend to notice and remember information that supports what we "
            "already believe.\n\n"
            "Deliberately look for evidence that could prove you wrong."
        ),
    },
    {
        "title": "Sunk Cost Fallacy",
        "body": (
            "Time or money already spent is gone whatever you decide next.\n\n"
            "Judge a decision by its future costs and benefits, not by what you have "
            "already put in."
        ),
    },
    {
        "title": "Hanlon's Razor",
        "body": (
            "Don't assume bad intent when carelessness or a misunderstanding "
            "explains the behaviour.\n\n"
            "It keeps conflicts smaller and conversations more useful."
        ),
    },
    {
        "title": "Margin of Safety",
        "body": (
            "Leave room for error in plans and estimates.\n\n"
            "Things take longer and go wrong more often than expected, so a buffer "
            "protects you."
        ),
    },
    {
        "title": "Regression to the Mean",
        "body": (
            "Extreme results tend to be followed by more average ones.\n\n"
            "Don't read too much into a single unusually good or bad outcome."
        ),
    },
    {
        "title": "Survivorship Bias",
        "body": (
            "We see the successes and miss the many cases that failed and went "
            "unnoticed.\n\n"
            "Ask what the full set of cases looks like, not just the visible ones."
        ),
    },
    {
        "title": "The Eisenhower Matrix",
        "body": (
            "Sort tasks by urgent and important.\n\n"
            "Important but not urgent work is where long-term progress usually "
            "comes from, so protect time for it."
        ),
    },
    {
        "title": "Chesterton's Fence",
        "body": (
            "Before removing a rule or system, find out why it was put there.\n\n"
            "If you can't see its purpose, understand it before you tear it down."
        ),
    },
    {
        "title": "Bayesian Thinking",
        "body": (
            "Start with a best estimate and update it as new evidence arrives.\n\n"
            "Strong beliefs should move when the facts do."
        ),
    },
    {
        "title": "Anchoring",
        "body": (
            "The first number or idea you hear shapes the judgments that follow.\n\n"
            "Form your own estimate before looking at someone else's."
        ),
    },
    {
        "title": "Systems Thinking",
        "body": (
            "Look at how the parts of a situation affect each other, not just the "
            "parts alone.\n\n"
            "Many problems come from the connections, not from one broken piece."
        ),
    },
]

WELCOME_MESSAGE = (
    "Welcome to Mental Models Daily.\n\n"
    "This bot sends you one mental model at a time, explained briefly.\n\n"
    "Commands:\n"
    "/model - get a random mental model\n"
    "/subscribe - get one model every day\n"
    "/unsubscribe - stop the daily message\n"
    "/help - show this message again"
)

# ---------------------------------------------------------------------------
# SUBSCRIBER STORAGE
# ---------------------------------------------------------------------------


def load_subscribers() -> set:
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_subscribers(subs: set) -> None:
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subs), f)


subscribers = load_subscribers()


def format_model(pick: dict) -> str:
    return f"🧠 {pick['title']}\n\n{pick['body']}"


# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(format_model(random.choice(MODELS)))


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        await update.message.reply_text("You're already subscribed.")
        return
    subscribers.add(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text(
        "Subscribed. You'll get one mental model a day. Send /unsubscribe to stop."
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in subscribers:
        await update.message.reply_text("You're not subscribed.")
        return
    subscribers.discard(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text("You've been unsubscribed.")


async def send_daily_model(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs once a day and sends one random model to every subscriber."""
    if not subscribers:
        return
    text = format_model(random.choice(MODELS))
    for chat_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as exc:
            logger.warning("Failed to send to %s: %s", chat_id, exc)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Use `export BOT_TOKEN=...` locally or the "
            "Variables tab on Railway."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("model", model))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Daily message at 09:00 UTC. Change the hour to suit your audience.
    application.job_queue.run_daily(send_daily_model, time=dtime(hour=9, minute=0))

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
