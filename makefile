init:
	pip install -r requirements.txt

lint:
	pylint --extension-pkg-whitelist=cv2 pi_turret

run:
	python -m pi_turret -c $(c)

dev:
	# python -m pi_turret.camera.picam_frames
	python -m pi_turret.test_scripts.face_tracking