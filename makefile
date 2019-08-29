init:
	pip install -r requirements.txt

lint:
	pylint pi_turret

run:
	python -m pi_turret -c $(c)

