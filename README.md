# EasyNode.PRO Validator Toolbox for Findora

## Findora Validator Toolbox
Here's our validator toolbox for the Findora network.  

This is a new product, there's a lot of enhancements yet to come but if you have any ideas put them into our [issues tracker](https://github.com/easy-node-pro/validatortoolbox_fra/issues)!

## Requirements
TBD, works well on all tested nodes atm, Ubuntu 20.04LTS & 22.04LTS

## Brand New Server Install of Findora
Currently we'll run the installer if `fn` is not present on your system. Clone the repository and run the app to get started:
```text
cd ~/ && git clone https://github.com/easy-node-pro/validatortoolbox_fra.git && cd validatortoolbox_fra && pip3 install -r requirements.txt --quiet && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Add to Existing Findora Server
You certainly can check out the package and run it just like anyone else, you'll want to update apt list first though and install python3-pip at a minimum. This will make sure everything is ready:
```text
cd ~/ && sudo apt install python3-pip -y && git clone https://github.com/easy-node-pro/validatortoolbox_fra.git && cd validatortoolbox_fra && pip3 install -r requirements.txt --quiet && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Run the Validator Toolbox
After installing you can use the following code for a termius/moba snippet and we also suggest using this full command to update and run each time you want to launch the toolbox:
```text
cd ~/validatortoolbox_fra/ && git pull && pip3 install -r requirements.txt --quiet && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Findora Menu
A management menu with validator information and commands provided by EasyNode.PRO, being built.
