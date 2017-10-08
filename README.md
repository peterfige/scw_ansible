# Scaleway Dynamic Inventory

It provides an executable script you can use with Ansible's /-i/ command line option.

# Configuration

Configuration can be change via environment variables.

Variable|Default|Description
--------|-------|-----------
`SCW_TOKEN`| | Your Scaleway access token (find how to get one https://developer.scaleway.com/#tokens-tokens-post)
`SCW_REGION` | `par1` | Scaleway region. Valid options as of 7.10.2017: `par1`, `ams1`
`SCW_DESTINATION_VARIABLE` | `public_ip` |  The ip address ansible will be using to access the node. Valid options: `public_ip`, `private_ip`. If you are running Ansible from outside Scaleway, then 'public_ip' makes the most sense. If you are running Ansible from within Scaleway, then perhaps you want to use the internal ip address, and should set this to 'private_ip'. When using `public_ip`, nodes without a public ip address are ignored.
`SCW_FILTER` | | Filter expressions, separated by `;`. Only nodes satisfying every filter expression are included. See filters below.
`SCW_EXCLUDE` | | Exclude expressions, separated by `;`. Nodes satisfying any exclude expression are excluded. See filters below.

# Groups

The results are automatically grouped by:
* node type, prefixed with `commercial_type_`, for example `commercial_type_VC1S`
* node architecture, prefixed with `arch_`, for example `arch_x86_64`
* host name, prefixed with `hostname_`, for example `hostname_master`
* node name, prefixed with `name_`, for example `name_master`
* security group, prefixed with `security_group_`, for example `security_group_ssh_only`

The server's tags are also used to create ansible groups. If the tag does not contain `:`, the tag is prefixed with `tag_` and
forms a group. If the tag is in the form of `environment:<something>` or `ansible:<something>` then the server will be part of the
group `<something>`.

# Node variables

All tags in the form of `<key>:<value>` are added as variables for the corresponding node.

# Filters, excludes

The set of nodes that are included in the results can be controlled by setting the `SCW_FILTER` and the `SCW_EXCLUDE` 
environment variables. Both take a `;` separate list of equality expressions. An equality expression takes the form of `<path>=<regexp>`:
* `<path>` is a `.` separated path to locate a value in the host variables of a node. 

  You can use host variables, defined via tags: if a node has a tag `deployment:test`, than `deployment=test` would be a feasible 
  filter equality expression.
  
  You can use values provided by the Scaleway API, prefixed with `scw`: for example `scw.image.name=Ubuntu` is a feasible
  filter equality expression.
 
* `<regexp>` is a python regular expression that will be searched against the value located by `<path>`. This means the
  regexp does not have to match the whole value, it can be anywhere in the value. If you want to force a complete match,
  use `^match_this$`.
  
Some examples:
```bash
# Ubuntu instances with ipv6 enabled
export SCW_FILTER=scw.image.name=Ubuntu;scw.enable_ipv6=true

# only tagged as deployment:test, exclude arm instances
export SCW_FILTER=deployment=test
export SCW_EXCLUDE=scw.arch=arm
```

