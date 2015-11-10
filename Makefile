bin = env/bin
python = $(bin)/python3
pip = $(bin)/pip

install-dev:
	pyvenv env
	$(pip) install -r requirements-dev.txt
	$(python) setup.py develop

install:
	pip3 install -r requirements.txt
	python3 setup.py install

clean:
	rm -r `$(python) <<< "from appdirs import user_data_dir; print(user_data_dir('Riley', 'Riley'))"`

test:
	$(bin)/py.test
