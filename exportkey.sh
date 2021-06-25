#!/bin/bash
#
# This script export a public ssh key to other nodes 
# to enable log to other nodes with ssh using its private key

if (( $# != 3 )); then
	echo "Usage: $0 PUBLIC_SSH_KEY USER NODES"
	exit 1
fi

public_key=$1
user=$2
nodes=$(hostlist -e $3)

for node in $nodes; do
	echo "Sharing public key to $user@$node"
	#ssh-copy-id -i $public_key $user@$IP
done
