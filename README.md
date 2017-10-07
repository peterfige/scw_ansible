# Scaleway Dynamic Inventory

It provides an executable script you can use with Ansible's /-i/ command line option.

# Configuration

Configuration can be change via environment variables.

Variable|Default|Description
--------|-------|-----------
`SCW_TOKEN`| | Your Scaleway access token (find how to get one https://developer.scaleway.com/#tokens-tokens-post)
`SCW_REGION` | `par1` | Scaleway region. Valid options as of 7.10.2017: `par1`, `ams1`
`SCW_DESTINATION_VARIABLE` | `public_ip` |  The ip address ansible will be using to access the node. Valid options: `public_ip`, `private_ip`. If you are running Ansible from outside Scaleway, then 'public_ip' makes the most sense. If you are running Ansible from within Scaleway, then perhaps you want to use the internal ip address, and should set this to 'private_ip'. When using `public_ip`, nodes without a public ip address are ignored.

# Examples

## Ams1

```
# SCW_REGION=ams1 ansible hareng -m shell -a "uptime"
hareng | SUCCESS | rc=0 >>
 23:18:08 up 26 min,  2 users,  load average: 0.08, 0.02, 0.01
```

## Default (par1)

```
# ansible fletan -m shell -a "uptime"
fletan | SUCCESS | rc=0 >>
 23:19:38 up 526 days,  2:38,  1 user,  load average: 2.70, 2.48, 2.44
```

