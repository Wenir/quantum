. venv/bin/activate
if [[ "$(python main.py test1.json)" = "$(cat test_result1)" ]];
then
	echo test ok
else
	echo fail!!!!!!!
fi
