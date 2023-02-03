# Findora Toolbox - Web UI 
Created by ⚡ EasyNode.PRO ⚡  

A web interface for the [findora-toolbox](https://github.com/FindoraNetwork/findora-toolbox) for Findora Validators.  

## Web Stats
Would you like to go to a web page on your validator server to get your stats? This is it! 

![findora-toolbox-web ui shot](/src/static/img/findora-web-main.png)

## Install Web UI
Install the [findora-toolbox](https://github.com/FindoraNetwork/findora-toolbox) repo to get the web UI.

## Launch Web UI
After you install, you'll need to configure your server. Run the following code to launch the app. On the first launch it'll ask for a username, password, and port to use for your web service. We suggest using a high port number (in the 30000 - 65500 range to keep it off scanners) and possibly locking down your firewall to your home/work IPs for extra security (don't forget to open the port # you pick on your firewall/ufw setup as well). Here's the code to launch the app.py:  
```text copy
python3 ~/findora-toolbox-web/web/src/app.py
```

## Run Web UI
You can run the UI when you'd like it, or set it up as a service to always run. Here's how to do either option.  

### Web UI with `tmux`
We suggest launching your session in `tmux` if you would like to keep it running. If you don't have tmux installed, run: `sudo apt install tmux` to get it onto your system. Then you can run a tmux session and launch the app.py:  
```text copy
tmux
python3 ~/findora-toolbox/web/src/app.py
```

Once the app launches you can close the session terminal and it'll keep running, or you can press `ctrl+b d` to detach from it and continue using your system normally while it runs in the background. If you reboot you will need to restart the tmux session and app.py or if you'd like to re-attach to the running tmux, simply type `tmux attach` to reconnect. `ctrl+c` will stop your running app.py if it's on your screen showing information.

### Web UI as a service
We've included a service file you can customize for your system. Copy the file to system.d then edit the username if you're not running as `servicefindora`:  
```text copy
sudo cp ~/findora-toolbox/web/src/bin/findora-web.service /etc/systemd/system/
```

#### Customize Username
If you use a different username, update any of the places you see `servicefindora` in the service file to be your username if different. You can edit the service file with:  
```text copy
sudo nano /etc/systemd/system/findora-web.service
``` 

Enable and start your service with:  
```text copy
sudo systemctl enable findora-web
sudo systemctl start findora-web
```

Now it'll simply always run as a service. Verify your service is running with:  
```text copy
sudo service findora-web status
```

Verify it looks similar to the output below:  

![findora-web-stats service](/src/static/img/findora-web-status.png)

## Update Web UI
If you're using either method, simply go into the findora-toolbox-web folder, run a `git pull` and then restart tmux or your service. You'll have to stop your old tmux session if you're using that method. If you setup the service file run:  
```text copy
cd ~/findora-toolbox-web/ && git pull && sudo service findora-web restart
```

## Fail2Ban
If you're already using [Fail2Ban from our Guides](https://guides.easynode.pro/admin#fail2ban) to secure ssh, you can add a security layer to the port number you choose above.  

Here's an example of creating a file to secure findora-toolbox-web on port 29843. Edit the new file with:  
```text copy
sudo nano /etc/fail2ban/jail.d/findora-toolbox-web.conf
```

Then add the following lines to your new file, save and exit:  
```text copy
[findora-toolbox-web-auth]
enabled = true
port    = 29843
filter  = findora-toolbox-web-auth
logpath  = /var/log/auth.log
maxretry = 3
bantime = 120
```

Then you'll need to reload fail2ban to apply your changes:  
```text copy
sudo systemctl restart fail2ban
```

## Update User/Password/Port
To change your username, password or port edit ~/.findora.env with an editor, for example:  
```text copy
nano ~/.findora.env
```

Edit the info you'd like to change, save and exit. Then restart your web server to begin using updated options.

## HTTPS
The issue with using HTTPS is it has to be run on a domain name and we're simply going by IP/Port here.  

You can run a reverse proxy with nginx and build this into a container behind SSL/Domain if you'd like but this is for private personal usage so we're not providing instructions or support for SSL at this time. We highly suggest locking the port down to your home/work IP if you're going to have it open and running 24/7.