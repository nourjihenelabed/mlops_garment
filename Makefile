PYTHON=python
ENV_NAME=venv
REQUIREMENTS=requirements.txt
PYLINT_MIN_SCORE = 6.0
FLAKE8_MAX_COMPLEXITY = 12
FLAKE8_MAX_LINE_LENGTH = 120

#1.Env Configuration
setup:
	@echo "Creating the virtual environment and installing dependencies.."
	@virtualenv  $(ENV_NAME)
	@. $(ENV_NAME)/bin/activate && pip install -r $(REQUIREMENTS)
#Code quality, automatic code formatting , code security 
.PHONY: setup-dev
setup-dev:
	@echo "Installing development dependencies..."
	@. $(ENV_NAME)/bin/activate && pip install -r requirements-dev.txt
	@echo " Development dependencies installed!"

.PHONY: setup-all
setup-all: setup setup-dev
	@echo "Full environment ready (production + dev)!"

.PHONY: black
black:
	@echo "Formatting code with Black..."
	@$(ENV_NAME)/bin/black *.py
	@echo "Black formatting completed!"
.PHONY: pylint-gate
pylint-gate:
	@echo " Running Pylint Quality Gate (min score: $(PYLINT_MIN_SCORE))..."
	@$(ENV_NAME)/bin/pylint *.py --fail-under=$(PYLINT_MIN_SCORE) || \
		( echo 'Pylint Gate Failed!'; exit 1 )
	@echo "Pylint Gate Passed!"

.PHONY: flake8-gate
flake8-gate:
	@echo " Running Flake8 Formatting Gate..."
	@$(ENV_NAME)/bin/flake8 main.py \
		--count \
		--statistics \
		--max-complexity=$(FLAKE8_MAX_COMPLEXITY) \
		--max-line-length=$(FLAKE8_MAX_LINE_LENGTH) || \
		( echo ' Flake8 Gate Failed!'; exit 1 )
	@echo "Flake8 Gate Passed!"

.PHONY: bandit-gate
bandit-gate:
	@echo "Running Bandit Security Gate..."
	@$(ENV_NAME)/bin/bandit -r main.py model_pipeline.py --quiet || \
		( echo ' Bandit Gate Failed!'; exit 1 )
	@echo "Bandit Gate Passed!"
.PHONY: ci
ci: black pylint-gate flake8-gate bandit-gate
	@echo " All Quality Gates Passed Successfully!"

data:
	@echo "Data preparation ..."
	@$(ENV_NAME)/bin/python main.py --prepare
	@echo "Finished Data preparation :D "

.PHONY: train
train: data
	@echo "Training the model ..."
	@$(ENV_NAME)/bin/python main.py --train
	@echo "Finished Training :D "

.PHONY: test
test:
	@echo "Running all tests..."
	@. $(ENV_NAME)/bin/activate && PYTHONPATH=. pytest tests/unit --maxfail=1 --disable-warnings -q
	@. $(ENV_NAME)/bin/activate && PYTHONPATH=. pytest tests/integration --maxfail=1 --disable-warnings -q
	@. $(ENV_NAME)/bin/activate && PYTHONPATH=. pytest tests/functional --maxfail=1 --disable-warnings -q
	@echo "All tests completed!"

.PHONY: coverage
coverage:
	@echo "Running tests with coverage..."
	@. $(ENV_NAME)/bin/activate && pytest --cov=./ --cov-report=term-missing


.PHONY: notebook
notebook:
	@echo "Starting Jupyter Notebook..."
	@. $(ENV_NAME)/bin/activate && jupyter notebook
	@echo "Jupyter Notebook stopped :D"

.PHONY: all
all: setup ci data train test
	@echo " All steps completed!"

.PHONY: pipeline
pipeline:
	@echo "Which step do you want to run? [prepare/train/evaluate/all]"
	@read STEP; \
	case $$STEP in \
	prepare) $(ENV_NAME)/bin/python main.py --prepare ;; \
	train) $(ENV_NAME)/bin/python main.py --train ;; \
	evaluate) $(ENV_NAME)/bin/python main.py --evaluate ;; \
	all) $(ENV_NAME)/bin/python main.py --all ;; \
	*) echo "Invalid step"; exit 1 ;; \
	esac

.PHONY: test-report
test-report:
	@echo "Running all tests and saving report..."
	@export PYTHONPATH=$$PWD && . $(ENV_NAME)/bin/activate && pytest --junitxml=test-results.xml
	@echo "Test report saved as test-results.xml"
.PHONY: test-report
test-report:
	@echo "Running all tests and saving HTML report..."
	@export PYTHONPATH=$$PWD && . $(ENV_NAME)/bin/activate && \
	pytest --html=test-report.html --self-contained-html
	@echo " HTML Test report saved as test-report.html"
