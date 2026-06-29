.PHONY: help install collect train test api dashboard frontend seed report memoir check-data docker clean

help:
	@echo "DeforestWatch-DRC — commandes disponibles :"
	@echo "  make install    Installe les dépendances Python"
	@echo "  make seed       Génère les données de démo (synthétiques)"
	@echo "  make collect    Lance la collecte de données (GEE + météo)"
	@echo "  make train      Entraîne les 3 modèles ML"
	@echo "  make test       Lance la suite de tests pytest"
	@echo "  make api        Démarre l'API FastAPI (port 8000)"
	@echo "  make dashboard  Démarre le dashboard Streamlit (port 8501)"
	@echo "  make frontend   Démarre le frontend React (port 5173)"
	@echo "  make report     Génère le rapport de synthèse"
	@echo "  make memoir     Génère le mémoire académique (.docx)"
	@echo "  make check-data Vérifie les vraies données dans data/raw/"
	@echo "  make docker     Build + run via docker-compose"

install:
	pip install -r requirements.txt

seed:
	python -m scripts.seed_demo

collect:
	python -m scripts.collect_data

train:
	python -m scripts.train_all

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

api:
	uvicorn src.api.main:app --reload --port 8000

dashboard:
	streamlit run streamlit_app/app.py --server.port 8501

frontend:
	cd frontend && npm install && npm run dev

report:
	python -m scripts.generate_report

memoir:
	python -m scripts.generate_memoir

check-data:
	python -m scripts.check_real_data

docker:
	docker-compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage spark-warehouse
