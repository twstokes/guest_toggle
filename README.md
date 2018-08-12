## Reasoning
I was looking for a way to segment some IoT devices from my main network and disable their network connections on demand programmatically. The Guest Network feature on the router does a good job of segmenting the network, so I wanted a way to turn the guest network's interface off and on based upon conditions.

_Example scenario_: You have cloud-based IoT cameras and want to cease all traffic when you're home.

### What this does

This puts toggling any interface on the router behind an HTTP endpoint. Since an interface is created when a guest network is enabled, we can now enable and disable that network whenever we want.

## Getting started

1. Install [Asuswrt-Merlin](https://asuswrt.lostrealm.ca/) on your Asus router
2. Create a guest network and disable intranet access
3. Enable SSH access in Administration
4. Generate a passwordless SSH keypair  
	
   An example running from the `ssh` directory:  
   `ssh-keygen -t rsa -b 2048 -N "" -f id_rsa -C guest_toggle`

   1. On the router's web interface, put the contents of id_rsa.pub in Administration -> Authorized Keys
   2. 	**Keep the private key private!**
   3. To verify everything's good to go, you should be able to run `ssh -i [private key you generated] admin@[router ip]` and get a prompt

   _Note:_ For convenience this project turns off host key checking to keep it entirely non-interactive. A best practice is to leave it enabled. You'd only need to verify the key once.


### Running via Docker from the repo root example:

```
docker build . -t twstokes:guest_toggle

docker run -it --rm  \
		-e ROUTER_USER=admin \
		-e ROUTER_HOSTNAME=192.168.1.1 \
		-e ROUTER_INTERFACE=wl0.1 \
		-p 8000:5000 \
		-v $(pwd)/ssh:/root/.ssh twstokes:guest_toggle
```

### Docker Compose example:

```
version: '3'

services:
  guest-toggle:
    build: .
    volumes:
      - ./ssh:/root/.ssh
    ports:
      - 8000:5000
    environment:
      - ROUTER_USER=admin
      - ROUTER_HOSTNAME=192.168.1.1
      - ROUTER_INTERFACE=wl0.1
```

`docker-compose build`  
`docker-compose up`

## Usage

In these examples we'll assume Docker is locally running the examples from above.

- Enabling the interface: `curl localhost:8000/enable`  
- Disabling the interface: `curl localhost:8000/disable`  
- Getting the state: `curl localhost:8000/state`

  
####Verification:

SSHing into the router and running `ifconfig` will show whether the interface is enabled (visible in the list), or disabled (not visible in the list). You can also check the state of `/sys/class/net/[interface name]/flags`.

## More info:

Running `ebtables -L` (a sibling to `iptables`) on the router should show you the rules in place for interfaces. In my case, the VLAN the router had created was properly dropping any FORWARDed traffic from the untrusted interface because the "Access Intranet" setting for the guest network was set to "Off".

#### Why I couldn't accomplish this via `iptables`:  

I found that I could drop / allow new traffic at will by adding and removing FORWARD rules, but couldn't affect established TCP connections. The IoT cameras would happily keep transferring data over their existing connections to the cloud and I'd be at mercy of the default timeout. I wanted this to work immediately.
