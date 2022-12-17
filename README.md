[![Codacy Badge](https://app.codacy.com/project/badge/Grade/aa50cae790bd4319a9cca9c6500301f6)](https://www.codacy.com/gh/easy-node-pro/validatortoolbox_fra/dashboard?utm_source=github.com&utm_medium=referral&utm_content=easy-node-pro/validatortoolbox_fra&utm_campaign=Badge_Grade)
[![Codacy Security Scan](https://github.com/easy-node-pro/validatortoolbox_fra/actions/workflows/codacy.yml/badge.svg?branch=main)](https://github.com/easy-node-pro/validatortoolbox_fra/actions/workflows/codacy.yml)
[![Discord Badge](https://img.shields.io/badge/chat-discord-purple?logo=discord)](https://discord.gg/Rcz5T6D9CV)
[![Stake Now Badge](https://img.shields.io/badge/stake-findora-purple)](https://bit.ly/easynodefra)

# EasyNode.PRO Validator Toolbox for Findora

## Findora Validator Toolbox

![image](https://guides.easynode.pro/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ffindora_loader.be572de6.png&w=1080&q=75)

Here's the [EasyNode.PRO](https://easynode.pro) validator toolbox for the Findora network.

### Requirements

Findora suggests the following server requirements:
Minimum: 8GB RAM, 2 Core CPU (2.90GHz per core), 100GB Hard Disk
Recommended: 16GB RAM, 4 Core CPU (2.90Ghz per core), 300GB Hard Disk

## Full documentation

If you're not sure what requirements are needed for the server, how to setup the firewall or how to install docker, our [full guide](https://guides.easynode.pro/findora/toolbox) will help you through setting up a server with Findora Toolbox.

We've also got a full breakdown of the components and how they work on the [Toolbox Docs Site](https://guides.easynode.pro/findora/tb_docs).

## Quick start guide for power users

### Fresh server installation

Currently we'll run the installer if `fn` is not present on your system. Clone the repository and run the app to get started:

```text
cd ~/ && sudo apt install python3-pip -y && git clone https://github.com/easy-node-pro/validatortoolbox_fra.git && cd validatortoolbox_fra && pip3 install -r requirements.txt --quiet && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

### Add to an existing Findora server

You certainly can check out the package and run it just like anyone else. Run the same command as above to start setup.

### Migrate to a new server

You can use the toolbox to easily migrate to a new server. We suggest starting with a fresh server and letting it sync up on the blockchain.

Once you're at that point, perform the following:

- On the new server, make a folder named `~/migrate` in your home directory. We suggest `mkdir ~/migrate`
- On the new server, use a transfer app to drop your `tmp.gen.keypair` and `priv_validator_key.json` files into the new `~/migrate` folder.
- At this point you are ready to convert the new server to your uploaded keys.
- On the old server, shut off the old server now to **avoid double signing**.
- On the new server, run validator toolbox and you'll now see option #888 to migrate server. Run this option and you will be converted over to the keys in migrate and brought back online.

### Run the Validator Toolbox Menu after Installation

After installing you can use the following code for a termius/moba snippet and we also suggest using this full command to update and run each time you want to launch the toolbox:

```text
cd ~/validatortoolbox_fra/ && git pull && pip3 install -r requirements.txt --quiet && cd ~/ && python3 ~/validatortoolbox_fra/src/app.py
```

## Future Enhancements

This is a new product, there's a lot of enhancements yet to come but if you have any ideas put them into our [issues tracker](https://github.com/easy-node-pro/validatortoolbox_fra/issues)!

- Move Stats out of options 1 & 2 and onto the front page
-
