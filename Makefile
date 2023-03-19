dev:
	# pip freeze | xargs pip uninstall -y
	pip install --upgrade pip setuptools build
	pip install pip-tools -r requirements_dev.txt

format:
	black .
	isort . --profile black

update-dev:
	pip-compile --resolver=backtracking --no-header -o requirements.txt pyproject.toml
	pip-compile --resolver=backtracking --no-header --extra dev -o requirements_dev.txt pyproject.toml
  
aws-deploy-prod:
	chmod +x scripts/deploy_stack.sh
	scripts/deploy_stack.sh
