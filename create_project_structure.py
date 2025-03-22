import os
import subprocess

def create_directory_structure():
    # Project root directory name
    root_dir = "Household_service_2XXXXXXX"
    
    # Directory structure with files
    structure = {
        # Root level files
        "README.md": "# Household Services Application - V2\n\nModern Application Development II Project",
        ".gitignore": """
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Vue
.DS_Store
node_modules
/dist
.env.local
.env.*.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.idea/
.vscode/
*.swp
*.swo
""",
        "requirements.txt": """
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
Flask-JWT-Extended==4.3.1
redis==3.5.3
celery==5.1.2
pytest==6.2.5
""",
        
        # Frontend structure
        "frontend/": {
            "public/": {
                "index.html": "<!DOCTYPE html><html><head><title>Household Services</title></head><body><div id='app'></div></body></html>"
            },
            "src/": {
                "main.js": "",
                "App.vue": "",
                "router/": {"index.js": ""},
                "store/": {"index.js": ""},
                "components/": {
                    "auth/": {
                        "Login.vue": "",
                        "Register.vue": ""
                    },
                    "admin/": {
                        "Dashboard.vue": "",
                        "UserManagement.vue": "",
                        "ServiceManagement.vue": ""
                    },
                    "customer/": {
                        "Dashboard.vue": "",
                        "ServiceRequest.vue": ""
                    },
                    "professional/": {
                        "Dashboard.vue": "",
                        "RequestManagement.vue": ""
                    }
                },
                "assets/": {
                    "styles/": {"main.css": ""}
                }
            }
        },
        
        # Backend structure
        "backend/": {
            "app.py": """
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)
""",
            "config.py": """
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///household_services.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""",
            "celery_worker.py": "",
            "models/": {
                "__init__.py": "",
                "user.py": "",
                "service.py": "",
                "request.py": "",
                "review.py": ""
            },
            "routes/": {
                "__init__.py": "",
                "auth.py": "",
                "admin.py": "",
                "customer.py": "",
                "professional.py": ""
            },
            "services/": {
                "__init__.py": "",
                "email_service.py": "",
                "cache_service.py": "",
                "export_service.py": ""
            },
            "tasks/": {
                "__init__.py": "",
                "reminder_tasks.py": "",
                "report_tasks.py": "",
                "export_tasks.py": ""
            },
            "utils/": {
                "__init__.py": "",
                "decorators.py": "",
                "validators.py": "",
                "helpers.py": ""
            },
            "templates/": {
                "email/": {
                    "reminder.html": "",
                    "monthly_report.html": ""
                }
            }
        },
        
        # Tests structure
        "tests/": {
            "__init__.py": "",
            "test_auth.py": "",
            "test_services.py": "",
            "test_tasks.py": ""
        }
    }

    def create_structure(base_path, structure):
        for item, content in structure.items():
            path = os.path.join(base_path, item)
            
            if isinstance(content, dict):
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

    # Create the root directory
    os.makedirs(root_dir, exist_ok=True)
    
    # Create the structure
    create_structure(root_dir, structure)
    
    # Initialize git repository
    try:
        os.chdir(root_dir)
        subprocess.run(["git", "init"])
        print("Git repository initialized successfully!")
    except Exception as e:
        print(f"Error initializing git repository: {e}")

    print(f"\nProject structure created successfully in {root_dir}/")
    print("\nNext steps:")
    print("1. Create and activate virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("\n2. Install requirements:")
    print("   pip install -r requirements.txt")
    print("\n3. Initialize Vue.js project:")
    print("   cd frontend")
    print("   vue create .")

if __name__ == "__main__":
    create_directory_structure() 