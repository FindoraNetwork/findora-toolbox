# EasyNode.PRO Validator Toolbox for Findora

## Findora Validator Toolbox
Here's our validator toolbox for the Findora network.

## Requirements
TBD, works well on all tested nodes atm, Ubuntu 20.04LTS & 22.04LTS

## Brand New Server Install of Findora
Currently we'll run the installer if `fn` is not present on your system. Clone the repository and run the app to get started:
```text
cd ~/ && git clone https://github.com/easy-node-pro/validatortoolbox_fra.git && cd validatortoolbox_fra && pip3 install -r requirements.txt && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Add to Existing Findora Server
You certainly can check out the package and run it just like anyone else, you'll want to update apt list first though and install python3-pip at a minimum. This will make sure everything is ready:
```text
cd ~/ && sudo apt install python3-pip -y && git clone https://github.com/easy-node-pro/validatortoolbox_fra.git && cd validatortoolbox_fra && pip3 install -r requirements.txt && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Run the Validator Toolbox
After installing, run the validator toolbox anytime with the following command:
```text
python3 ~/validatortoolbox_fra/src/app.py
```

## Upgrade the Toolbox
When you upgrade, remember to always run the requirements.txt file to add any upgrades.
```text
cd ~/validatortoolbox_fra/ && git pull && pip3 install -r requirements.txt
```

## Termius/Moba Snippet
Want to check and setup upgrades every time you launch? Run the following block:
```text
cd ~/validatortoolbox_fra/ && git pull && pip3 install -r requirements.txt && cd ~/ && python3 ~/validatortoolbox/src/app.py
```

## Findora Menu
A management menu with validator information and commands provided by EasyNode.PRO, being built.
