import interactions 
import tokens

bot = interactions.Client(
    token=tokens.token,
    default_scope='755573870789918780'
)

@bot.command()
async def badge(ctx: interactions.CommandContext):
    await ctx.send("here's the monthly interaction ...bitch!")

bot.start()