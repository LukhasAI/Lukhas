#!/usr/bin/env python3
"""
LUKHAS Commercial API Deployment Script
Packages commercial APIs for independent deployment
"""

import json
import shutil
from pathlib import Path
from typing import Dict


class CommercialAPIDeployer:
    def __init__(self, source_root: str = ".", target_root: str = "./deployments"):
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
        self.apis = {
            "dream_commerce": {
                "name": "LUKHAS Dream Commerce API",
                "version": "1.0.0",
                "description": "Commercial API for dream generation and analysis",
                "dependencies": ["asyncio", "dataclasses", "typing"],
                "optional_deps": ["numpy", "torch"],
                "includes_personality": True,
            },
            "memory_services": {
                "name": "LUKHAS Memory Services API",
                "version": "1.0.0",
                "description": "Enterprise memory storage and retrieval",
                "dependencies": ["asyncio", "dataclasses", "typing", "datetime"],
                "optional_deps": ["redis", "postgresql"],
                "includes_personality": False,
            },
            "consciousness_platform": {
                "name": "LUKHAS Consciousness Platform API",
                "version": "1.0.0",
                "description": "Consciousness simulation and awareness tracking",
                "dependencies": ["asyncio", "dataclasses", "typing", "enum"],
                "optional_deps": ["numpy", "scikit-learn"],
                "includes_personality": False,
            },
        }

    def deploy_all(self):
        """Deploy all commercial APIs"""
        print("🚀 LUKHAS Commercial API Deployment")
        print("=" * 50)

        # Create deployments directory
        self.target_root.mkdir(exist_ok=True)

        # Deploy each API
        for api_name, api_config in self.apis.items():
            print(f"\n📦 Deploying {api_config['name']}...")
            self.deploy_api(api_name, api_config)

        # Create master deployment manifest
        self.create_deployment_manifest()

        print("\n✅ Deployment complete!")
        print(f"📁 APIs deployed to: {self.target_root}")

    def deploy_api(self, api_name: str, config: Dict):
        """Deploy a single API"""
        # Create API deployment directory
        api_dir = self.target_root / api_name
        api_dir.mkdir(exist_ok=True)

        # Copy API files
        source_api = self.source_root / "commercial_apis" / api_name
        if source_api.exists():
            shutil.copytree(source_api, api_dir / api_name, dirs_exist_ok=True)

        # Create setup.py
        self.create_setup_py(api_dir, api_name, config)

        # Create requirements.txt
        self.create_requirements_txt(api_dir, config)

        # Create README
        self.create_readme(api_dir, api_name, config)

        # Create Docker file
        self.create_dockerfile(api_dir, api_name)

        # Create example usage
        self.create_example(api_dir, api_name)

        # Strip personality if not included
        if not config["includes_personality"]:
            self.strip_personality_imports(api_dir)

        print(f"  ✓ Deployed to {api_dir}")

    def create_setup_py(self, api_dir: Path, api_name: str, config: Dict):
        """Create setup.py for the API"""
        setup_content = f'''"""
Setup script for {config['name']}
"""

from setuptools import setup, find_packages

setup(
    name="{api_name.replace('_', '-')}",
    version="{config['version']}",
    description="{config['description']}",
    author="LUKHAS AI",
    author_email="api@lukhas.ai",
    packages=find_packages(),
    install_requires={config['dependencies']},
    extras_require={{
        'advanced': {config['optional_deps']}
    }},
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
'''
        (api_dir / "setup.py").write_text(setup_content)

    def create_requirements_txt(self, api_dir: Path, config: Dict):
        """Create requirements.txt"""
        requirements = "\n".join(config["dependencies"])
        (api_dir / "requirements.txt").write_text(requirements)

        # Create optional requirements
        optional = "\n".join(config["optional_deps"])
        (api_dir / "requirements-advanced.txt").write_text(optional)

    def create_readme(self, api_dir: Path, api_name: str, config: Dict):
        """Create README.md"""
        readme_content = f"""# {config['name']}

{config['description']}

## Installation

```bash
pip install -r requirements.txt
```

For advanced features:
```bash
pip install -r requirements-advanced.txt
```

## Quick Start

```python
from {api_name} import *

# See examples/example.py for detailed usage
```

## API Documentation

See [API_DOCS.md](API_DOCS.md) for full documentation.

## License

Commercial License - Contact sales@lukhas.ai

## Support

- Email: support@lukhas.ai
- Documentation: https://docs.lukhas.ai/{api_name}
"""
        (api_dir / "README.md").write_text(readme_content)

    def create_dockerfile(self, api_dir: Path, api_name: str):
        """Create Dockerfile"""
        dockerfile_content = f"""FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY {api_name} {api_name}
COPY examples examples

EXPOSE 8000

CMD ["python", "-m", "{api_name}.server"]
"""
        (api_dir / "Dockerfile").write_text(dockerfile_content)

    def create_example(self, api_dir: Path, api_name: str):
        """Create example usage file"""
        examples_dir = api_dir / "examples"
        examples_dir.mkdir(exist_ok=True)

        if api_name == "dream_commerce":
            example = '''"""
Dream Commerce API Example
"""

import asyncio
from dream_commerce import DreamCommerceAPI, DreamRequest

async def main():
    # Initialize API
    api = DreamCommerceAPI()
    await api.initialize()
    
    # Generate a dream
    request = DreamRequest(
        prompt="flying through space",
        style="creative",
        length="medium"
    )
    
    response = await api.generate_dream(request)
    print(f"Generated Dream: {response.content}")
    print(f"Symbols: {response.symbols}")
    print(f"Themes: {response.themes}")

if __name__ == "__main__":
    asyncio.run(main())
'''
        elif api_name == "memory_services":
            example = '''"""
Memory Services API Example
"""

import asyncio
from memory_services import MemoryServicesAPI, MemoryStore, MemoryQuery

async def main():
    # Initialize API
    api = MemoryServicesAPI(storage_backend="standard")
    
    # Store a memory
    memory = MemoryStore(
        content="Important meeting notes",
        type="text",
        tags=["meeting", "important"],
        importance=0.9
    )
    
    memory_id = await api.store(memory)
    print(f"Stored memory: {memory_id}")
    
    # Search memories
    query = MemoryQuery(
        query="meeting",
        limit=10
    )
    
    results = await api.retrieve(query)
    print(f"Found {len(results)} memories")

if __name__ == "__main__":
    asyncio.run(main())
'''
        else:  # consciousness_platform
            example = '''"""
Consciousness Platform API Example
"""

import asyncio
from consciousness_platform import (
    ConsciousnessPlatformAPI,
    ConsciousnessLevel,
    ReflectionRequest
)

async def main():
    # Initialize API
    api = ConsciousnessPlatformAPI(
        consciousness_level=ConsciousnessLevel.ENHANCED
    )
    
    # Get consciousness state
    state = await api.get_state()
    print(f"Consciousness Level: {state.level.value}")
    print(f"Awareness Scores: {state.awareness_scores}")
    
    # Perform reflection
    reflection = ReflectionRequest(
        topic="The meaning of existence",
        depth=3
    )
    
    result = await api.reflect(reflection)
    print(f"Insights: {result['insights']}")

if __name__ == "__main__":
    asyncio.run(main())
'''

        (examples_dir / "example.py").write_text(example)

    def strip_personality_imports(self, api_dir: Path):
        """Remove personality imports from non-personality APIs"""
        # In production, this would scan files and remove lukhas_personality imports
        pass

    def create_deployment_manifest(self):
        """Create master deployment manifest"""
        manifest = {
            "deployment_version": "1.0.0",
            "deployment_date": str(Path.cwd()),
            "apis": {},
        }

        for api_name, config in self.apis.items():
            manifest["apis"][api_name] = {
                "name": config["name"],
                "version": config["version"],
                "location": str(self.target_root / api_name),
                "includes_personality": config["includes_personality"],
            }

        manifest_path = self.target_root / "deployment_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"\n📋 Created deployment manifest: {manifest_path}")


def main():
    """Run the deployment script"""
    deployer = CommercialAPIDeployer()
    deployer.deploy_all()

    print("\n🎯 Next Steps:")
    print("1. Test each API independently")
    print(
        "2. Build Docker images: docker build -t lukhas-{api-name} deployments/{api-name}"
    )
    print("3. Push to registry: docker push lukhas-{api-name}")
    print("4. Deploy to cloud platform of choice")


if __name__ == "__main__":
    main()
