{{NAME}}  -  scroll site (offline)

HOW TO RUN
  Windows : double-click  start-windows.bat
            (a black window opens and your browser opens the site; keep the window open while viewing)
  Mac     : double-click  start-mac-linux.command   (first time: right-click > Open)
            needs Node.js or Python 3 installed

BEST EXPERIENCE
  - Use Chrome or Edge, full screen (F11).
  - Scroll slowly with the mouse wheel or trackpad. The hero is a scroll-driven video.
  - To see the mobile version: press F12, then the phone icon, and reload.

WHY NOT JUST OPEN index.html?
  The scroll video can only be scrubbed through a local web server, so the launcher starts a tiny one
  (no internet needed, nothing is installed). If a "node" folder is present it is a portable copy of Node.js for Windows.

FOLDER
  site/                  the website (static files)
  server.js / server.py  the tiny local servers (HTTP Range support)
  node/node.exe          portable Node.js (Windows, optional)
