# Data Collection Tool for Capstone

Data Collection Tool for Capstone Research

## Creating credentials to use the script

1. Go to the [Reddit console](https://www.reddit.com/prefs/apps)
2. Create an app and give it a name, use this redirect uri ("<http://www.example.com/unused/redirect/uri">), and designate it as a script
3. Grab the client id (located under the name you gave the app) and add `export REDDIT_CLIENT_ID=INSERT_VALUE` to your shell config file like .zshrc or just run the command in the shell
4. Grab the client secret and add `export REDDIT_CLIENT_SECRET=INSERT_VALUE` to your shell config file like .zshrc or just run the command in the shell

## For Cory

1. Make sure you're using Linux of some kind cuz I wasn't thinking about how to do stuff in Windows
2. Follow the instructions to get the credentials
3. `pip install praw afinn spacy scipy && python -m spacy download en`
4. Run ./example.sh and `chmod 777 example.sh` if it has permission isues (or just look at the files in the data folder cause this script takes a damn brick, they're from a run of the command within example.sh on Nov 29)
5. Mess around
6. Note post statistics are relative to other posts not to comments within them
