install:
	python3 setup.py install

devinstall:
	python3 setup.py develop

clean:
	rm -r `python3 <<< "from appdirs import user_data_dir; print(user_data_dir('Riley', 'Riley'))"`
