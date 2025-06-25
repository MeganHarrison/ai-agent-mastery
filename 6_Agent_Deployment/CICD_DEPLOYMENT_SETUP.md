# CI/CD Deployment Setup Guide with GitHub

This guide walks you through setting up automatic deployments from GitHub Actions to your DigitalOcean droplet.

## Prerequisites

1. A DigitalOcean droplet with the application already deployed and running
2. SSH access to the droplet configured with a non-root user
3. GitHub repository with admin access to configure secrets
4. The project cloned on the droplet (path is configurable, e.g., `/home/deploy/dynamous`)

## Security Philosophy

This deployment setup follows a **separation of concerns** security model:
- **GitHub** only stores deployment mechanics (SSH keys, server location)
- **Your server** maintains all sensitive application secrets (API keys, database credentials)
- **No production secrets** are ever stored in GitHub

This approach ensures that even if your GitHub account is compromised, your production secrets remain secure on your server.

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository settings under Settings → Secrets and variables → Actions:

### 1. `DIGITALOCEAN_HOST`
- **Description**: The IP address or domain name of your DigitalOcean droplet
- **Example**: `192.168.1.100` or `your-server.example.com`
- **How to find**: In DigitalOcean dashboard or run `curl ifconfig.me` on the droplet

### 2. `DIGITALOCEAN_USERNAME`
- **Description**: The SSH username for your droplet (DO NOT use root)
- **Example**: `deploy`, `appuser`, or any custom username you created
- **Security Note**: Create a dedicated deployment user with limited permissions

### 3. `DIGITALOCEAN_SSH_KEY`
- **Description**: The private SSH key for accessing your droplet (WITHOUT passphrase)
- **Format**: Full private key including headers
- **How to generate**:
  ```bash
  # Generate a new key WITHOUT passphrase (-N "")
  ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key -N ""
  
  # Copy the public key to your droplet
  ssh-copy-id -i ~/.ssh/github_deploy_key.pub your-username@your-droplet-ip
  
  # Test the key works
  ssh -i ~/.ssh/github_deploy_key your-username@your-droplet-ip "echo 'Key works!'"
  
  # Get the private key content for GitHub secret
  cat ~/.ssh/github_deploy_key
  ```
- **Important**: When copying the private key to GitHub secrets, make sure it includes the final newline character
- **Security Note**: Use a dedicated deploy key without passphrase for automation

### 4. `DEPLOYMENT_PATH`
- **Description**: The absolute path to your project on the server
- **Example**: `/home/deploy/dynamous` or `/opt/apps/dynamous`
- **Default**: If using default setup, typically `/home/username/dynamous`
- **Note**: Must be an absolute path, not relative

### Note on GITHUB_TOKEN
- **Automatically Provided**: GitHub Actions automatically provides a `GITHUB_TOKEN` for each workflow run
- **No Manual Setup Required**: You do NOT need to create this as a secret
- **Permissions**: The automatic token has permissions to access your repository
- **Security**: This token is short-lived and scoped to the specific workflow run

## Environment Variables (Server-Side Management)

**IMPORTANT**: All sensitive environment variables are managed directly on your server, NOT in GitHub secrets. This provides better security separation.

### Setting Up Environment Variables on Your Server

1. **SSH into your server**:
   ```bash
   ssh deploy@your-droplet-ip
   ```

2. **Navigate to deployment directory**:
   ```bash
   cd /path/to/dynamous/6_Agent_Deployment
   ```

3. **Create your `.env` file**:
   ```bash
   nano .env
   ```

4. **Add your environment variables**:
  ```
  # LLM Configuration
  LLM_PROVIDER=openai
  LLM_BASE_URL=https://api.openai.com/v1
  LLM_API_KEY=sk-your-actual-api-key
  LLM_CHOICE=gpt-4o-mini
  VISION_LLM_CHOICE=gpt-4o-mini
  
  # Embedding Configuration
  EMBEDDING_PROVIDER=openai
  EMBEDDING_BASE_URL=https://api.openai.com/v1
  EMBEDDING_API_KEY=sk-your-actual-api-key
  EMBEDDING_MODEL_CHOICE=text-embedding-3-small
  
  # Database Configuration
  DATABASE_URL=postgresql://username:password@hostname:5432/database_name
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_SERVICE_KEY=your-service-key
  SUPABASE_ANON_KEY=your-anon-key
  
  # RAG Pipeline Configuration
  RAG_PIPELINE_TYPE=local
  RUN_MODE=continuous
  RAG_PIPELINE_ID=prod-rag-pipeline
  RAG_WATCH_DIRECTORY=/app/rag-documents
  
  # Search Configuration (optional)
  BRAVE_API_KEY=your-brave-api-key
  SEARXNG_BASE_URL=http://searxng:8080
  
  # Frontend Configuration
  VITE_SUPABASE_URL=https://your-project.supabase.co
  VITE_SUPABASE_ANON_KEY=your-anon-key
  VITE_AGENT_ENDPOINT=https://api.yourdomain.com/api/pydantic-agent
  VITE_ENABLE_STREAMING=true
  
  # Deployment Configuration (for cloud with Caddy)
  AGENT_API_HOSTNAME=api.yourdomain.com
  FRONTEND_HOSTNAME=app.yourdomain.com
  LETSENCRYPT_EMAIL=your-email@example.com
  
  # Environment
  ENVIRONMENT=production
  ```

## Setting Up GitHub Repository Secrets

1. Navigate to your repository on GitHub
2. Go to Settings → Secrets and variables → Actions
3. Select "Repository secrets" (not Environment secrets)
4. Click "New repository secret" for each secret
5. Enter the name exactly as shown above
6. Paste the value
7. Click "Add secret"

### Required Repository Secrets Summary:
- `DIGITALOCEAN_HOST` - Your server's IP or domain
- `DIGITALOCEAN_USERNAME` - Non-root SSH username
- `DIGITALOCEAN_SSH_KEY` - Private SSH key for deployment (NO passphrase)
- `DEPLOYMENT_PATH` - Absolute path to project on server

Note: Do NOT create a `GITHUB_TOKEN` secret - it's automatically provided by GitHub Actions.

## Initial Server Setup

Before enabling CI/CD, ensure your server is properly configured:

### 1. Create a Deployment User (Security Best Practice)

```bash
# SSH as root initially
ssh root@your-droplet-ip

# Create a new user for deployments
adduser deploy  # or your preferred username

# Add user to docker group
usermod -aG docker deploy

# Grant sudo privileges (if needed for your deployment)
usermod -aG sudo deploy

# Switch to the new user
su - deploy
```

### 2. Set Up SSH Key for the Deployment User

```bash
# As the deploy user, create .ssh directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add your deployment public key
nano ~/.ssh/authorized_keys
# Paste the public key that corresponds to your GitHub secret
chmod 600 ~/.ssh/authorized_keys
```

### 3. Clone and Set Up the Project

```bash
# As the deploy user
cd ~
git clone https://github.com/your-username/dynamous.git

# Navigate to deployment directory
cd ~/dynamous/6_Agent_Deployment

# Create initial .env file with your configuration
nano .env  # Paste your environment variables

# Set proper permissions
chmod 600 .env  # Only the deploy user can read

# Do initial deployment
python deploy.py --type cloud

# Verify deployment
docker compose ps
curl http://localhost:8001/health
```

### 4. Configure Firewall (Optional but Recommended)

```bash
# Allow SSH
sudo ufw allow 22

# Allow HTTP and HTTPS (for Caddy)
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

## Deployment Workflow

The CI/CD pipeline works as follows:

1. **Trigger**: Push to `main` branch or manual workflow dispatch
2. **Test Phase**: Runs all tests in parallel:
   - Python unit tests
   - Backend linting (Flake8)
   - Frontend linting (ESLint)
   - Frontend E2E tests (Playwright)
   - Docker container builds
   - Security analysis
3. **Deployment Phase** (only if all tests pass):
   - SSH into DigitalOcean droplet as deployment user
   - Pull latest code changes
   - Verify `.env` file exists (deployment fails if missing)
   - Create backup of current `.env` file
   - Stop current deployment gracefully
   - Start new deployment with existing environment variables
   - Verify health checks
   - Report deployment status

**Important**: The deployment process NEVER overwrites your `.env` file. All sensitive configuration remains on your server.

## Managing Environment Variables

Since environment variables are managed on the server, here's how to update them:

### Updating Environment Variables

```bash
# SSH into your server
ssh deploy@your-droplet-ip

# Navigate to deployment directory
cd /path/to/dynamous/6_Agent_Deployment

# Edit environment variables
nano .env

# Restart services to apply changes
python deploy.py --down --type cloud
python deploy.py --type cloud
```

### Environment Variable Backups

The deployment process automatically creates timestamped backups:
```bash
# View backups
ls -la .env.backup.*

# Restore from backup if needed
cp .env.backup.20240115_143022 .env
```

## Manual Deployment Trigger

You can manually trigger a deployment from GitHub Actions:

1. Go to Actions tab in your repository
2. Select "CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Choose branch: `main`
5. Deploy option: `true` (or `false` to run tests only)
6. Click "Run workflow"

## Monitoring Deployments

### During Deployment
- Watch the GitHub Actions logs in real-time
- The deployment script provides detailed progress updates
- Health checks verify each service starts correctly

### After Deployment
SSH into your server and check:

```bash
# View running containers
cd ~/dynamous/6_Agent_Deployment
docker compose ps

# View logs
docker compose logs -f agent-api
docker compose logs -f rag-pipeline
docker compose logs -f frontend

# Check service health
curl http://localhost:8001/health
```

## Rollback Procedure

If a deployment fails or causes issues:

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Navigate to project
cd ~/dynamous

# Rollback to previous commit
git log --oneline -10  # Find the previous good commit
git reset --hard <commit-hash>

# Redeploy
cd 6_Agent_Deployment
python deploy.py --down --type cloud
python deploy.py --type cloud
```

## Security Best Practices

1. **SSH Keys**: Use dedicated deployment keys, not personal keys
2. **Secrets Rotation**: Rotate tokens and keys regularly
3. **Least Privilege**: Always use a dedicated deployment user, never root
4. **Network Security**: Configure firewall rules on DigitalOcean
5. **HTTPS Only**: Always use HTTPS for production deployments
6. **Environment Isolation**: Never commit .env files or secrets to the repository
7. **Separation of Concerns**: GitHub only has deployment access, not access to production secrets

### Security Benefits of This Approach

- **Reduced Attack Surface**: GitHub compromise doesn't expose production secrets
- **Audit Trail**: All environment changes happen directly on the server with SSH logs
- **Principle of Least Privilege**: CI/CD only has permissions it needs (deploy code, not read secrets)
- **Easy Secret Rotation**: Update secrets on the server without touching CI/CD configuration
- **Compliance**: Many security standards require secrets to be managed outside of CI/CD systems

## Troubleshooting

### SSH Connection Fails
- Verify the SSH key is correctly formatted in GitHub secrets
- Check droplet firewall allows GitHub Actions IPs
- Ensure the public key is in `~/.ssh/authorized_keys` on the droplet

### Git Pull Fails
- Verify GITHUB_TOKEN has correct permissions
- Check the repository URL in the droplet's git config
- Ensure the token hasn't expired

### SSH "Permission denied (publickey)" Error
- **Most Common Cause**: SSH key missing final newline character
- **Solution**: The workflow now automatically adds a newline, but double-check your key
- **How to verify locally**:
  ```bash
  # Your key should work with this exact command:
  ssh -i ~/.ssh/github_deploy_key your-username@your-server-ip "echo 'test'"
  ```
- **Key format check**: Run `ssh-keygen -lf ~/.ssh/github_deploy_key` - should show key fingerprint

### Deployment Fails with ".env file not found"
- This is a safety feature - the deployment requires a pre-existing .env file
- SSH into the server and create the .env file as shown in the setup section
- Ensure the file has proper permissions: `chmod 600 .env`

### Other Deployment Failures
- Check Docker daemon is running: `systemctl status docker`
- Verify disk space: `df -h`
- Ensure deployment user has docker permissions: `groups deploy`
- Review service logs for specific errors

### Services Don't Start
- Verify all required environment variables are set
- Check database connectivity
- Ensure external services (Supabase, OpenAI) are accessible
- Review health check endpoints

## Advanced Configuration

### Staging Environment
To add a staging environment:

1. Create a new droplet for staging
2. Add staging-specific secrets (prefix with `STAGING_`)
3. Modify the deployment workflow to support environment selection
4. Use branch protection rules to control deployments

### Blue-Green Deployments
For zero-downtime deployments:

1. Run new containers alongside old ones
2. Verify new containers are healthy
3. Switch traffic to new containers
4. Remove old containers

### Deployment Notifications
Add notifications to Slack/Discord:

```yaml
- name: Send notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment ${{ job.status }}'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Maintenance

### Regular Tasks
- Review deployment logs weekly
- Update dependencies monthly
- Rotate secrets quarterly
- Test rollback procedure regularly

### Monitoring Recommendations
- Set up uptime monitoring (e.g., UptimeRobot)
- Configure log aggregation (e.g., Datadog, New Relic)
- Implement error tracking (e.g., Sentry)
- Monitor resource usage on DigitalOcean

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DigitalOcean Droplet Guides](https://docs.digitalocean.com/products/droplets/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [CI/CD Best Practices](https://www.digitalocean.com/community/tutorials/an-introduction-to-ci-cd-best-practices)