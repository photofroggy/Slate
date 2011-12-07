==========
Slate
==========

Slate is a bot for **dAmn**, deviantART's chatrooms.

Slate is built in **Python** using `reflex`_, `stutter`_, and `dAmn Viper`_.

.. _`reflex`: https://photofroggy.github.com/reflex/index.html
.. _`stutter`: https://github.com/photofroggy/stutter
.. _`dAmn Viper`: https://photofroggy.github.com/dAmnViper/index.html

================
Setting up slate
================
Setting up Slate is pretty simple.

------------
Requirements
------------
To run **Slate**, you must first install `Python 2.7`_ or better and
`twisted 11.0.0`_ or better. These two things are required for Slate to work
properly.

.. _`Python 2.7`: http://python.org/download/
.. _`twisted 11.0.0`: http://twistedmatrix.com/trac/wiki/Downloads

------------------
Download
------------------
If you have git installed, you can download the current revision of slate via
the terminal or command line. All you have to do is cd to the folder you want
to have slate stored in, and type the following::
    
    git clone git@github.com:photofroggy/Slate.git

Otherwise, you can download the latest release at *website*.

------------------
Setting up the bot
------------------
The best way to set up slate is to just run it and follow the instructions the
program gives you. If you installed slate's requirements properly, you should
be able to do this from the terminal or command line using the following
command when you are in the bot's folder::
    
    launch.py

You will then be asked to configure the bot.

Note that part of this involves authorizing the application with the deviantART
account you wish to use the bot with. To do this you will have to copy a link
that the program will give you, and visit this in your web browser while logged
in as your bot. Then confirm that slate is allowed to access your account.

This is a bit arduous, but there isn't really a good way around this.

---------------
Running the bot
---------------
As noted above, to run the bot, all you have to do is run the file `launch.py`.

---------------------
Reconfiguring the bot
---------------------
To reconfigure the bot, you can run the file `launch.py` with an additional
argument `--config`. So, for example, in the command line you would type::
    
    launch.py --config

From here you can change your bot's setup.


==========
DISCLAIMER
==========

Disclaimer::

		Slate is in no way affiliated with or endorsed by deviantART.com.
	This is not an official service of deviantART.com. This is an independent
	project created by Henry Rapley:
		<http://photofroggy.deviantart.com>
	
		THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
	APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
	HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
	OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
	THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
	PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
	IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
	ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

