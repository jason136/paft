# Paft Usage

To run the bot simply clone the repository and create the token.py file in the same location as Paft.py. 
Insert your Discord application client id to the file in the following structure.   

  ```python 
  token = 'YOUR DISCORD BOT API HERE'
  rapid_api_key = 'OPTIONAL RAPID API KEY HERE' 
  saucenao_key = 'OPTIONAL SAUCENAO API KEY HERE' 
  ```
  
After this is done simply run the Paft.py script and if all relevant modules are installed the bot should come online. 

To see what the bot does see the commands in the main file and cogs, or type ^help in a discord server it's active in. 

## Warning and Note about the future

This bot runs with the discord.py wrapper class for the Discord API, which has since been archived. 
The creator has said he does not intend to ever implement slash commands, so when the Discord API makes message content by privileged only this bot will most likely break. 
It is unlikely I'll do anything as ambitious as rewriting the entire bot so that'll just have to be the end of it sadly. 
