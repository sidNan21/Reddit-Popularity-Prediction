# Predicting Comment Popularity within Online Communities using Multiclass Classification

Multiclass classification for comment popularity using [sklearn](https://scikit-learn.org/stable/). Comment data primarily fetched using PRAW, from different user-created discussion boards from https://www.reddit.com/.

## How to perform experiments yourself:

### Downloading and installing dependencies

1. Have Python-3.x (latest stable version preferrably) installed (may be done via: `pip3 install -r requirements.txt`)
2. Have the latest Jupyter Notebook (classic of JupyterLab) installed, see: https://jupyter.org/install.html

### Creating credentials to use the script

1. Go to the [Reddit console](https://www.reddit.com/prefs/apps)
2. Create an app and give it a name, use this redirect uri ("<http://www.example.com/unused/redirect/uri">), and designate it as a script
3. Grab the client id (located under the name you gave the app) and add `export REDDIT_CLIENT_ID=INSERT_VALUE` to your shell config file like .zshrc or just run the command in the shell
4. Grab the client secret and add `export REDDIT_CLIENT_SECRET=INSERT_VALUE` to your shell config file like .zshrc or just run the command in the shell
5. You will know it works if `REDDIT_CLIENT_SECRET` and `REDDIT_CLIENT_ID` both show up as environment variables (which may show up as keys in `os.environ` in Python).

## Acknowledgements:

This project was done by Cory Kim and Siddharth Nanda, computer science students in the University of Virginia School of Engineering, under the guidance of Professor N. Rich Nguyen. It was directly inspired by ["Hacking the Hivemind:
Predicting Comment Karma on Internet Forums"](http://cs229.stanford.edu/proj2014/Daria%20Lamberson,Leo%20Martel,%20Simon%20Zheng,Hacking%20the%20Hivemind.pdf): a 2014 research paper by Daria Lamberson, Leo Martel, and Simon Zheng at Stanford University.
