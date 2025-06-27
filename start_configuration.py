#!/usr/bin/env python3
"""
Dynamous Agent Deployment Configuration Script

This script helps configure custom domains for the Dynamous AI Agent system.
It copies the render.yaml_production template and replaces domain placeholders
with your actual custom domain.
"""

import os
import re
import shutil
import sys
from pathlib import Path


def validate_domain(domain):
    """Validate domain name format."""
    # Basic domain validation regex
    domain_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    if not domain_pattern.match(domain):
        return False
    
    # Check length
    if len(domain) > 253:
        return False
    
    # Check for valid TLD
    if '.' not in domain:
        return False
    
    return True


def get_domain_input():
    """Get and validate domain input from user."""
    print("🌐 Dynamous Agent Deployment - Domain Configuration")
    print("=" * 55)
    print()
    print("This script will configure your custom domain for the Dynamous AI Agent system.")
    print("The domain will be used for:")
    print("  • Frontend web application")
    print("  • Agent API service (api subdomain)")
    print("  • OAuth redirect URLs") 
    print("  • Application base URLs")
    print()
    
    while True:
        domain = input("Enter your custom domain (e.g., myapp.com): ").strip().lower()
        
        if not domain:
            print("❌ Domain cannot be empty. Please try again.")
            continue
        
        # Remove protocol if provided
        domain = domain.replace('https://', '').replace('http://', '')
        
        # Remove trailing slash
        domain = domain.rstrip('/')
        
        if validate_domain(domain):
            return domain
        else:
            print(f"❌ Invalid domain format: {domain}")
            print("   Please enter a valid domain name (e.g., myapp.com, subdomain.example.org)")


def copy_and_configure_template(domain):
    """Copy template and replace domain placeholders."""
    template_file = Path("render.yaml_production")
    output_file = Path("render.yaml")
    
    if not template_file.exists():
        print(f"❌ Template file {template_file} not found!")
        print("   Make sure you're running this script from the project root directory.")
        sys.exit(1)
    
    print(f"\n📄 Copying {template_file} to {output_file}...")
    
    # Read template content
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace domain placeholders
    print(f"🔄 Replacing YOUR_CUSTOM_DOMAIN with {domain}...")
    content = content.replace('YOUR_CUSTOM_DOMAIN', domain)
    
    # Write configured file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully created {output_file}")
    return output_file


def configure_blueprint_files(domain):
    """Configure blueprint .env files from .env.example templates with domain placeholders."""
    blueprints_dir = Path("blueprints")
    
    if not blueprints_dir.exists():
        print(f"📝 Note: {blueprints_dir} directory not found, skipping blueprint configuration.")
        return
    
    blueprint_templates = [
        ("frontend-env.env.example", "frontend-env.env"),
        ("agent-api-env.env.example", "agent-api-env.env"), 
        ("rag-pipeline-env.env.example", "rag-pipeline-env.env")
    ]
    
    print(f"\n📄 Configuring blueprint environment files from templates...")
    
    for template_filename, output_filename in blueprint_templates:
        template_file = blueprints_dir / template_filename
        output_file = blueprints_dir / output_filename
        
        if not template_file.exists():
            print(f"⚠️  Template {template_file} not found, skipping...")
            continue
            
        print(f"🔄 Creating {output_file} from {template_file}...")
        
        # Read template content
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace domain placeholders
        content = content.replace('YOUR_CUSTOM_DOMAIN', domain)
        
        # Write configured file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Generated blueprint .env files with domain: {domain}")


def print_dns_instructions(domain):
    """Print DNS configuration instructions."""
    print(f"\n🔧 DNS Configuration Instructions for {domain}")
    print("=" * 60)
    print()
    print("To complete the setup, configure your DNS with these records:")
    print()
    print("📌 Frontend Domain Records:")
    print(f"   Type: CNAME, Name: @, Target: dynamous-frontend.onrender.com")
    print(f"   Type: CNAME, Name: www, Target: dynamous-frontend.onrender.com")
    print()
    print("📌 Agent API Domain Records:")
    print(f"   Type: CNAME, Name: api, Target: dynamous-agent-api.onrender.com")
    print()
    print("📌 Alternative A Record Setup:")
    print(f"   Type: A, Name: @, Target: 216.24.57.1")
    print(f"   Type: CNAME, Name: www, Target: dynamous-frontend.onrender.com")
    print(f"   Type: CNAME, Name: api, Target: dynamous-agent-api.onrender.com")
    print()
    print("⚠️  Important DNS Notes:")
    print("   • Remove any existing AAAA records (IPv6)")
    print("   • DNS propagation can take 5-60 minutes")
    print("   • If using Cloudflare, set SSL/TLS to 'Full' mode")
    print("   • Set Cloudflare proxy status to 'DNS Only' initially")
    print()


def print_deployment_instructions():
    """Print next steps for deployment."""
    print("🚀 Next Steps - Deployment")
    print("=" * 30)
    print()
    print("1. Configure your DNS records (see instructions above)")
    print()
    print("2. Update environment variables in Render Dashboard:")
    print("   • Go to each service → Settings → Environment")
    print("   • Use the generated .env files in blueprints/ directory:")
    print("     - frontend-env.env for Frontend service")
    print("     - agent-api-env.env for Agent API service") 
    print("     - rag-pipeline-env.env for RAG Pipeline service")
    print("   • Copy-paste the environment variables from these files")
    print("   • Update placeholder values (API keys, database URLs, etc.)")
    print()
    print("3. Deploy to Render:")
    print("   • Push to your Git repository")
    print("   • Connect repository to Render")
    print("   • Use the generated render.yaml for deployment")
    print()
    print("4. Verify domains in Render Dashboard:")
    print("   • Go to Frontend Service → Settings → Custom Domains")
    print("   • Click 'Verify' next to your main domain")
    print("   • Go to Agent API Service → Settings → Custom Domains") 
    print("   • Click 'Verify' next to your api subdomain")
    print("   • Wait for TLS certificate issuance for both services")
    print()


def check_gitignore():
    """Check and update .gitignore if needed."""
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        return
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_items = []
    if 'render.yaml' not in content:
        missing_items.append('render.yaml')
    if 'blueprints/frontend-env.env' not in content:
        missing_items.append('blueprints/*.env files')
    
    if missing_items:
        print(f"\n📝 Note: Consider adding these to .gitignore:")
        for item in missing_items:
            print(f"   • {item}")
        print("   This prevents configured files from being committed to the repository.")


def main():
    """Main configuration script."""
    try:
        # Get domain from user
        domain = get_domain_input()
        
        # Copy template and configure
        output_file = copy_and_configure_template(domain)
        
        # Configure blueprint files
        configure_blueprint_files(domain)
        
        # Print DNS instructions
        print_dns_instructions(domain)
        
        # Print deployment instructions
        print_deployment_instructions()
        
        # Check .gitignore
        check_gitignore()
        
        print("\n🎉 Configuration completed successfully!")
        print(f"   Your configured deployment file: {output_file}")
        print(f"   Your frontend domain: https://{domain}")
        print(f"   Your API domain: https://api.{domain}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Configuration cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during configuration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()