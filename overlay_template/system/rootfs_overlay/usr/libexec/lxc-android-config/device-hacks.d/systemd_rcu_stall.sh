# systemd-cgroup has a tendency to rcu stall during poweroff
echo 1 > /proc/sys/kernel/panic_on_rcu_stall
