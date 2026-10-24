#!/bin/sh
# Own only this chain/jump; never flush an existing host firewall.
set -eu
iptables=/usr/sbin/iptables
chain=POLYIA_INGRESS
case "${1:-}" in
    start)
        if ! "$iptables" -w -n -L "$chain" >/dev/null 2>&1; then
            "$iptables" -w -N "$chain"
        fi
        if ! "$iptables" -w -C "$chain" -i enp0s6 -p tcp -m multiport --dports 80,443 -m conntrack --ctstate NEW -j ACCEPT 2>/dev/null; then
            "$iptables" -w -A "$chain" -i enp0s6 -p tcp -m multiport --dports 80,443 -m conntrack --ctstate NEW -j ACCEPT
        fi
        if ! "$iptables" -w -C INPUT -j "$chain" 2>/dev/null; then
            "$iptables" -w -I INPUT 1 -j "$chain"
        fi
        ;;
    stop)
        while "$iptables" -w -C INPUT -j "$chain" 2>/dev/null; do
            "$iptables" -w -D INPUT -j "$chain"
        done
        if "$iptables" -w -C "$chain" -i enp0s6 -p tcp -m multiport --dports 80,443 -m conntrack --ctstate NEW -j ACCEPT 2>/dev/null; then
            "$iptables" -w -D "$chain" -i enp0s6 -p tcp -m multiport --dports 80,443 -m conntrack --ctstate NEW -j ACCEPT
        fi
        if "$iptables" -w -n -L "$chain" >/dev/null 2>&1; then
            "$iptables" -w -X "$chain"
        fi
        ;;
    *)
        echo 'Usage: polyia-hosting-firewall start|stop' >&2
        exit 2
        ;;
esac
