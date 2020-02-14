# DDNS Whitelist Generator

The DDNS Whitelist Generator is a security-minded Python 3 script designed to help homelabbers "expose" services for easy external access via your domain name *without* making them available to the general public.

The script generates a whitelist configuration snippet for your Nginx reverse proxy that contains both the whitelist itself and a deny all rule. You can include this snippet in a site block so that only the whitelisted IPs are allowed access (other IPs will receive a 403 Permission Denied error).

The script has also been designed to figure out what IP address is associated with user-provided domains. For homelabbers who have a domain name configured via DDNS, this allows us to whitelist ourselves (and/or any homelabbing friends) automatically - there is no need to go in an update your whitelist every time you or your friends have to restart the modem.

I am using unRAID and the User Scripts plugin to schedule and run this automatically/periodically, but it should be usable on other systems as long as you set up your config.json correctly.

## Getting Started

The jist of running this project is:

1. Clone project
2. Set up a `config.json` file with the CIDRs/domains you want whitelisted
3. Schedule the script to run on a regular (and realtively frequent) basis
4. Configure your Nginx-based reverse proxy to include the `whitelist.conf` file the script will output

### Setting up the config.json file

You can copy the sample file to get started:

```
cp config.json.sample config.json
```

Modify your new `config.json` file using your preferred editor. There are 3 sections in the file you need to set up, below are samples:

```
  "static_ips": [
    "192.168.0.1/16",
    "123.45.79.1/32"
  ],
```

Put the static CIDR ranges you need to whitelist here. You'll want to include your LAN, and may consider adding additional CIDRs for places you commonly access your services from that have a static CIDR (maybe your school or office).

```
  "dynamic_addresses":[
    "google.com",
    "mycompany.net"
  ],
```

This section is for domain names you want automatically updated when their IP changes. This is the main reason I wrote the script in the first place - if you have friends or family you want to whitelist, you can have their access automatically renewed when their IP changes. They do need DDNS set up on their end for this to work, but there are free options you can use to make this happen.

```"whitelist_path": "/mnt/user/appdata/whitelists/"```

This is simply where on the server running this script you want the script to save the whitelist it generates. Do not include the filename (that's hard-coded as `whitelist.conf` for now), just the directories.


### Installing on unRAID

*This setup uses Python 3, the [Nginx Proxy Manager](https://forums.unraid.net/topic/76460-support-djoss-nginx-proxy-manager/), and the [CA User Scripts](https://forums.unraid.net/topic/48286-plugin-ca-user-scripts/) plugin. The [NerdPack](https://forums.unraid.net/topic/35866-unraid-6-nerdpack-cli-tools-iftop-iotop-screen-kbd-etc/) plugin can help you install Python 3 if you don't already have it.*

#### Download project and schedule in User Scripts plugin

1. Save the project to a static location on your server, probably somewhere most users on your system don't have access.
2. Set up `config.json` (see above for details)
3. Go to the User Scripts plugin and add a bash script that executes the Python script (see sample below):
4. Click Run Script to verify it's working. You should see `DDNS whitelist generated and/or updated.` if it was successful.
5. Check the contents of the `whitelist.conf` file the script outputs to make sure it added the CIDR ranges you wanted correctly.


```
#!/bin/bash
python3 /mnt/user/appdata/scripts/ddns-whitelist-generator/ddns-whitelist-generator.py
```

You should also be able to use other schedulers like cron itself if you prefer; the basic idea is the same.

#### Configure Nginx Proxy Manager to use whitelist

1. Edit your Nginx Proxy Manager container and click *+Add another Path, Port, Variable, Label, or Device*
    * Select *Path* for the config type
    * Give it a recognizeable name like *Whitelists*
    * Enter *whitelists* for the container path
    * Enter the `whitelist_path` from your `config.json` file for the *Host path*
2. Save and start your Nginx Proxy Manager container
3. Navigate to the Nginx Proxy Manager webUI and edit the proxy host you want to use this whitelist
4. Select Advanced and paste an include directive for the whitelist.
    * If you didn't change the paths and names used in these instructions, that include line will be: `include /whitelists/whitelist.conf;`


This must be done per host you want using the whitelist, as far as I'm aware there is no way to bulk add this include line.


### Installing on other generic Nginx system

*Your system needs Nginx and Python 3.*

I've more or less designed this to work on the unRAID setup described above, but I tried to make the script mostly system-agnostic. It should still work on a standard Linux box running your Nginx reverse proxy; the process would basically be:

1. Save the script to a static cron-accessible path and set up your `config.json` file
2. Add a cron job to run the script at the frequency of your preference
3. Use `include` statements in your Nginx site blocks to make them utilize the `whitelist.conf` file (pay attention to where you set `whitelist_path` in the script config)

You'll probably need to test your Nginx config and restart to apply the changes. Depending on your system, that might look something like:


```
nginx -t
systemctl restart Nginx
```


## Validate the Install

Verify access is limited to your whitelisted IPs! You can usually get an IP that isn't whitelisted through a VPN connection, public wifi, or by using your cell data to connect.