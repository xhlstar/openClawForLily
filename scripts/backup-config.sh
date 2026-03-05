#!/bin/bash

# OpenClaw Configuration Backup Script
# This script creates a safe backup of OpenClaw configuration files

set -e

CONFIG_DIR="/home/allen/.openclaw"
BACKUP_DIR="/home/allen/.openclaw/workspace/config-backup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Starting OpenClaw configuration backup..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create a safe version of openclaw.json (remove sensitive info)
echo "Creating safe version of openclaw.json..."
cp "$CONFIG_DIR/openclaw.json" "$BACKUP_DIR/openclaw.original.$TIMESTAMP.json"

# Create sanitized version (remove API keys and tokens)
python3 -c "
import json
import sys

with open('$CONFIG_DIR/openclaw.json', 'r') as f:
    config = json.load(f)

# Remove sensitive information
if 'models' in config and 'providers' in config['models']:
    for provider in config['models']['providers']:
        if 'apiKey' in config['models']['providers'][provider]:
            config['models']['providers'][provider]['apiKey'] = 'REMOVED_FOR_SECURITY'

if 'gateway' in config and 'auth' in config['gateway'] and 'token' in config['gateway']['auth']:
    config['gateway']['auth']['token'] = 'REMOVED_FOR_SECURITY'

with open('$BACKUP_DIR/openclaw.safe.$TIMESTAMP.json', 'w') as f:
    json.dump(config, f, indent=2)
"

# Copy other important non-sensitive files
echo "Backing up other configuration files..."

# List of files to backup (non-sensitive)
FILES_TO_BACKUP=(
    "exec-approvals.json"
    "cron/jobs.json"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$CONFIG_DIR/$file" ]; then
        echo "  Backing up $file..."
        cp "$CONFIG_DIR/$file" "$BACKUP_DIR/$(basename "$file").$TIMESTAMP"
    fi
done

# Create a summary file
echo "Creating backup summary..."
cat > "$BACKUP_DIR/backup-summary.$TIMESTAMP.txt" << EOF
OpenClaw Configuration Backup
=============================
Timestamp: $(date)
Backup directory: $BACKUP_DIR

Files backed up:
- openclaw.original.$TIMESTAMP.json (original with sensitive info)
- openclaw.safe.$TIMESTAMP.json (sanitized version)
$(for file in "${FILES_TO_BACKUP[@]}"; do 
    if [ -f "$CONFIG_DIR/$file" ]; then
        echo "- $(basename "$file").$TIMESTAMP"
    fi
done)

Notes:
- Original files contain sensitive information (API keys, tokens)
- Safe versions have sensitive information removed
- Do not commit original files to version control
EOF

echo "Backup completed successfully!"
echo "Backup files saved to: $BACKUP_DIR"
echo "Summary: $BACKUP_DIR/backup-summary.$TIMESTAMP.txt"

# Optional: Commit to git if in workspace directory
if [ -d "/home/allen/.openclaw/workspace/.git" ]; then
    echo ""
    echo "Would you like to commit the safe configuration to git? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        cd "/home/allen/.openclaw/workspace"
        
        # Copy safe config to workspace
        cp "$BACKUP_DIR/openclaw.safe.$TIMESTAMP.json" "config/openclaw.safe.json"
        
        # Add and commit
        git add config/openclaw.safe.json
        git commit -m "Update safe configuration backup - $TIMESTAMP"
        
        echo "Committed safe configuration to git."
    fi
fi