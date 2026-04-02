import os

base_dir = r"c:\Users\User\Downloads\Proyecto-Analisis-Territorial-main"
services = ["configuration", "ingestion", "audit-trace", "gateway"]

structure = [
    "app",
    "app/api",
    "app/api/endpoints",
    "app/core",
    "app/models",
    "app/schemas",
    "app/services"
]

for service in services:
    service_path = os.path.join(base_dir, "Backend", service)
    for folder in structure:
        os.makedirs(os.path.join(service_path, folder), exist_ok=True)
        # Create __init__.py files
        init_file = os.path.join(service_path, folder, "__init__.py")
        with open(init_file, "w") as f:
            pass

    # Root __init__.py
    with open(os.path.join(service_path, "app", "__init__.py"), "w") as f:
        pass

# Create .env proxy
with open(os.path.join(base_dir, ".env"), "w") as f:
    f.write("""POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=territorial_db
POSTGRES_HOST=db_postgres
POSTGRES_PORT=5432
JWT_SECRET=supersecretkey12345
JWT_ALGORITHM=HS256
""")

print("Scaffolding complete.")
