# Cloud9 --> AMI 

Sometimes you have to develop code on a machine hosted in the cloud, like if you're spinning up an AMI or something. In the VIM vs EMACS wars I have left the battlefield. We invented graphics for a reason.

Anyway, here's how you can install the Cloud9 agent on an EC2 instance. Cloud9 is nifty because it doesn't cost any more than the underlying EC2 instance it runs on.

(Note: This only works for Linux, and not ARM-based arch)


## 1. Launch your AMI

Launch an EC2 instance into a VPC. The instance has to be reachable over the public internet. You should only be using this for development etc, so it will be okay to expose the instance to the internet and set the SG to only allow inbound traffic on p22. 

If this makes you nervous, restrict the IPs for which SSH traffic is accepted from the IP range of cloud9,
https://docs.aws.amazon.com/cloud9/latest/user-guide/ip-ranges.html

## 2. Configure your instance

You need to install,
* Python3
* Node.JS

You'll also need to know where nodeJS is installed on the instance.

## 3. Set up C9

1. Select the SSH option for C9
2. Copy the C9 public key to the ~/.ssh/authorized_keys file on your server
3. Paste the path to nodeJS where it says
4. Choose which directory you want to start into

## 4. Hit Open IDE

Cloud9 has to install some stuff on the instance for the IDE to work. Luckily for you, Cloud9 will do it all for you and you just have to click a few buttons. 

