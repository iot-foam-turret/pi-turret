init:
	pip install -r requirements.txt

lint:
	pylint --extension-pkg-whitelist=cv2 pi_turret

run:
	python -m pi_turret -c $(c)

