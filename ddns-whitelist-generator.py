import os
import json
import socket

def main():

    # This makes our working directory the same place this script is actually located
    # Which allows us to open config.json via its relative path (so we don't need to ask the user to provide the install location)
    script_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_path)

    # Your configuration options should be defined in config.json and are loaded here
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

    # This is one of the more likely steps somebody could miss on initial install so we catch this exception and report it before exiting
    except FileNotFoundError:
        print("No config.json file found. Refer to the config.json.sample file and README to set one up!")
        exit()

    # Make the target directory if it doesn't exist (otherwise we can't write to it later)
    if not os.path.exists(config['whitelist_path']):
        try:
          os.system("mkdir {0}".format(config['whitelist_path']))
        except:
           pass

    # Build a list of CIDRs to whitelist
    cidrs = []

    # Make each static CIDR range into an NGINX-compatible line eg "allow 192.168.0.0/16" and include newline break
    # These should already be formatted as CIDR ranges and include the necessary /16, /24, etc
    for ip in config['static_ips']:
        cidrs.append("allow "+ip+";\n")

    # Make each dynamic address into an NGINX-compatible line as above but use single-address CIDR with /32
    for domain in config['dynamic_addresses']:
        # First we need to use socket to check what the domain's IP address is
        ip = socket.gethostbyname(domain)
        cidrs.append("allow "+ip+"/32;\n")

    # We have all the CIDR ranges we want to whitelist, so add the deny all rule to the end of the list
    cidrs.append("deny all;")

    # And then write the result to the whiltelist file
    with open(config['whitelist_path']+"whitelist.conf", mode='wt') as whitelist:
        for line in cidrs:
            whitelist.write(line)

    # Restart nginx
    # Disabled for unraid version where this won't work... might find a docker command substitute
    # os.system("systemctl restart nginx")
    print("DDNS whitelist generated and/or updated.")

main()
