SWAP_PATH="/userdata/SWAP.img"
if [ -e "$SWAP_PATH" ]
then
	swapon "$SWAP_PATH"
fi
