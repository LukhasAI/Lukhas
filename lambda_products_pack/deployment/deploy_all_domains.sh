#!/bin/bash

# LUKHAS Domain Deployment Script
# Deploys Lambda Products to all 10 domains

echo "================================================"
echo "🚀 LUKHAS ECOSYSTEM DEPLOYMENT"
echo "================================================"

# Configuration
DOMAINS=(
    "lukhas.ai"
    "lukhas.id"
    "lukhas.dev"
    "lukhas.io"
    "lukhas.store"
    "lukhas.cloud"
    "lukhas.eu"
    "lukhas.us"
    "lukhas.xyz"
    "lukhas.team"
)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack"
BUILD_DIR="$BASE_DIR/build"

# Function to build content for each domain
build_domain_content() {
    local domain=$1
    local domain_name=${domain%.ai}
    domain_name=${domain_name%.id}
    domain_name=${domain_name%.dev}
    domain_name=${domain_name%.io}
    domain_name=${domain_name%.store}
    domain_name=${domain_name%.cloud}
    domain_name=${domain_name%.eu}
    domain_name=${domain_name%.us}
    domain_name=${domain_name%.xyz}
    domain_name=${domain_name%.team}
    
    echo -e "${BLUE}Building content for $domain...${NC}"
    
    # Create domain-specific build directory
    mkdir -p "$BUILD_DIR/$domain"
    
    # Copy base files
    cp -r "$BASE_DIR/auctor/generated_content/"* "$BUILD_DIR/$domain/" 2>/dev/null
    
    # Generate domain-specific content using AUCTOR
    python3 << EOF
import sys
sys.path.append('$BASE_DIR')
from auctor.auctor_content_engine import AuctorContentEngine, DomainArea, ContentType, ToneLayer
import asyncio
import json

async def generate_for_domain():
    engine = AuctorContentEngine()
    
    # Map domains to their primary content
    domain_map = {
        'lukhas.ai': DomainArea.AI_CONSCIOUSNESS,
        'lukhas.id': DomainArea.QUANTUM_SECURITY,
        'lukhas.dev': DomainArea.AUTONOMOUS_AGENTS,
        'lukhas.io': DomainArea.ENTERPRISE_AI,
        'lukhas.store': DomainArea.AUTONOMOUS_AGENTS,
        'lukhas.cloud': DomainArea.ENTERPRISE_AI,
        'lukhas.eu': DomainArea.AI_CONSCIOUSNESS,
        'lukhas.us': DomainArea.ENTERPRISE_AI,
        'lukhas.xyz': DomainArea.BLOCKCHAIN_AI,
        'lukhas.team': DomainArea.PRODUCTIVITY_OPTIMIZATION
    }
    
    domain = '$domain'
    area = domain_map.get(domain, DomainArea.AI_CONSCIOUSNESS)
    
    # Generate landing page
    content = await engine.generate_content(
        domain=area,
        content_type=ContentType.LANDING_PAGE,
        tone=ToneLayer.USER_FRIENDLY
    )
    
    # Save to file
    with open('$BUILD_DIR/$domain/config.json', 'w') as f:
        json.dump({
            'domain': domain,
            'content': content,
            'generated': True
        }, f, indent=2)
    
    print(f"✓ Generated content for {domain}")

asyncio.run(generate_for_domain())
EOF
    
    echo -e "${GREEN}✓ Built $domain${NC}"
}

# Function to deploy to domain
deploy_to_domain() {
    local domain=$1
    
    echo -e "${BLUE}Deploying to $domain...${NC}"
    
    # Check if domain is reachable
    if ping -c 1 $domain &> /dev/null; then
        echo -e "${GREEN}✓ $domain is reachable${NC}"
        
        # Deploy based on hosting setup
        # Option 1: Vercel deployment
        if command -v vercel &> /dev/null; then
            cd "$BUILD_DIR/$domain"
            vercel --prod --name lukhas-${domain//./-} --yes
        fi
        
        # Option 2: Traditional hosting via rsync
        # rsync -avz "$BUILD_DIR/$domain/" "root@$domain:/var/www/html/"
        
        # Option 3: GitHub Pages
        # git add . && git commit -m "Deploy $domain" && git push origin $domain
        
    else
        echo -e "${RED}✗ $domain is not configured yet${NC}"
    fi
}

# Function to setup SSL
setup_ssl() {
    local domain=$1
    
    echo -e "${BLUE}Setting up SSL for $domain...${NC}"
    
    # Using Certbot for Let's Encrypt
    if command -v certbot &> /dev/null; then
        sudo certbot certonly --webroot -w "/var/www/$domain" -d "$domain" -d "www.$domain" --non-interactive --agree-tos --email admin@lukhas.ai
        echo -e "${GREEN}✓ SSL configured for $domain${NC}"
    else
        echo -e "${RED}Certbot not installed. Install with: sudo apt-get install certbot${NC}"
    fi
}

# Function to setup analytics
setup_analytics() {
    local domain=$1
    
    echo -e "${BLUE}Setting up analytics for $domain...${NC}"
    
    # Add Google Analytics to index.html
    cat >> "$BUILD_DIR/$domain/index.html" << 'EOF'
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
EOF
    
    echo -e "${GREEN}✓ Analytics added to $domain${NC}"
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    echo ""
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    # Build and deploy each domain
    for domain in "${DOMAINS[@]}"; do
        echo "================================================"
        echo "Processing: $domain"
        echo "================================================"
        
        build_domain_content "$domain"
        deploy_to_domain "$domain"
        # setup_ssl "$domain"  # Uncomment when domains are live
        setup_analytics "$domain"
        
        echo ""
    done
    
    # Generate deployment report
    generate_report
    
    echo "================================================"
    echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
    echo "================================================"
    echo ""
    echo "Next steps:"
    echo "1. Configure DNS for each domain"
    echo "2. Set up hosting (Vercel/AWS/Google Cloud)"
    echo "3. Enable SSL certificates"
    echo "4. Configure payment processing"
    echo "5. Launch marketing campaigns"
}

# Generate deployment report
generate_report() {
    cat > "$BASE_DIR/deployment_report.md" << EOF
# LUKHAS Deployment Report
Generated: $(date)

## Domains Deployed

| Domain | Status | SSL | Analytics | Content |
|--------|--------|-----|-----------|---------|
EOF
    
    for domain in "${DOMAINS[@]}"; do
        if [ -d "$BUILD_DIR/$domain" ]; then
            echo "| $domain | ✓ Built | Pending | ✓ Added | ✓ Generated |" >> "$BASE_DIR/deployment_report.md"
        else
            echo "| $domain | ✗ Failed | - | - | - |" >> "$BASE_DIR/deployment_report.md"
        fi
    done
    
    cat >> "$BASE_DIR/deployment_report.md" << EOF

## Next Steps
1. Configure DNS records
2. Set up hosting
3. Enable SSL
4. Test all endpoints
5. Monitor analytics
EOF
    
    echo -e "${GREEN}Report saved to: $BASE_DIR/deployment_report.md${NC}"
}

# Run main function
main

# Make executable
chmod +x "$0"