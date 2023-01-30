# default power profile before repowerd triggers power hal
# without limiting the power draw it seems possible for hangups to occur waking up from suspend
INTERACTIVE_PATH_L=/sys/devices/system/cpu/cpu0/cpufreq/interactive
INTERACTIVE_PATH_B=/sys/devices/system/cpu/cpu4/cpufreq/interactive

echo 20000 > ${INTERACTIVE_PATH_L}/timer_rate
echo 20000 > ${INTERACTIVE_PATH_L}/timer_slack
echo 40000 > ${INTERACTIVE_PATH_L}/min_sample_time
echo 40000 > ${INTERACTIVE_PATH_L}/boostpulse_duration

echo 20000 > ${INTERACTIVE_PATH_B}/timer_rate
echo 20000 > ${INTERACTIVE_PATH_B}/timer_slack
echo 40000 > ${INTERACTIVE_PATH_B}/min_sample_time
echo 40000 > ${INTERACTIVE_PATH_B}/boostpulse_duration

echo 858000 > ${INTERACTIVE_PATH_L}/hispeed_freq
echo 85 > ${INTERACTIVE_PATH_L}/go_hispeed_load
echo "75 1170000:85" > ${INTERACTIVE_PATH_L}/target_loads
echo "19000 1274000:39000" > ${INTERACTIVE_PATH_L}/above_hispeed_delay

echo 1040000 > ${INTERACTIVE_PATH_B}/hispeed_freq
echo 99 > ${INTERACTIVE_PATH_B}/go_hispeed_load
echo "87 1664000:90" > ${INTERACTIVE_PATH_B}/target_loads
echo "79000 1248000:99000 1664000:19000" > ${INTERACTIVE_PATH_B}/above_hispeed_delay

echo 6 > /sys/power/cpuhotplug/max_online_cpu
