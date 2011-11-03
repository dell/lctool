This package depends on the 'stdcli' package. Install that first (it has identical install instructions, so you can also install it similar to the instructions below.) Also, you will need to install pywbem, which isnt in the default OS installs, but should be available in your OS.

To develop on RHEL6+:

1) ensure ~/.local/bin is on your PATH. add the following to your ~/.bashrc:

export PATH=$PATH:~/.local/bin

2) Then run the setuptoolsl setup.py (included):

$ python ./setup.py develop --user

This will install "symlinks" to your local directory in ~/.local/lib/python$VER/site-packages/.

Now, when you run the "lcctool" binary, it will run the copy in ~/.local/bin/ and will use the libraries from ~/.local/lib, even if you otherwise have a copy installed on your system. This also allows multiple people to each develop on one system and use their own local copy.



To develop on RHEL5:

RHEL5 doesnt have the nifty ~/.local/ trick, so only one copy can be installed on a machine for development purposes at a time.

$ python ./setup.py develop

This will install system symlinks pointing to your local directory.
