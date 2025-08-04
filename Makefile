terraform:
	@echo "🚀 Initializing Terraform, create GCP resources"
	cd terraform/
	terraform init
	terraform apply

terraform-destroy:
	@echo "🗑️ Destroying resources..."
	cd terraform/
	terraform destroy

mageai-start:
	@echo "🐳 Starting MageAI services..."
	cd my-mage-docker-quickstart
	./start.sh

web-service-start:
	@echo "🐳 Starting Docker services..."
	docker compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	

web-service-stop:
	@echo "🐳 Stopping Docker services..."
	docker compose down

mlflow-serve:
	@echo "run mlflow server"
	mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://DB_USER:DB_PASSWORD@DB_ENDPOINT:5432/DB_NAME --default-artifact-root gs://my-gcs-bucket