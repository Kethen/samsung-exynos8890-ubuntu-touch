tries=0
while [ -z "$(android_shell.sh lshal | grep -i 'android.hardware.light@2.0::ILight/default')" ]
do
	tries=$((tries + 1))
	if [ $tries -eq 120 ]
	then
		break
	fi
	sleep 0.5
done

if [ $tries -eq 120 ]
then
	echo lighthal is not ready after $tries retries
else
	echo light hal is ready after $tries retries
fi
