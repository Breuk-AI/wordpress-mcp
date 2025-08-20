# 🚀 WordPress MCP - Automated Deployment Guide

## Quick Deploy (While You're Busy with the Race Event)

I've set up everything for automatic deployment. Just run ONE command:

```batch
ONE_CLICK_DEPLOY.bat
```

This will:
1. ✅ Backup your current code
2. ✅ Apply all security fixes
3. ✅ Run tests
4. ✅ Commit changes
5. ✅ Push to GitHub
6. ✅ Get your green CI checkmark

## What Gets Deployed

### 🔒 Security Fixes (All Critical Issues Fixed)
- **Path Traversal Protection**: realpath validation, extension whitelist
- **Encrypted Authentication**: Fernet encryption, no plaintext
- **Input Validation**: XSS/SQLi/RCE prevention
- **Rate Limiting**: Token bucket + sliding window
- **Session Management**: Proper pooling, SSL enforcement

### 📊 Production Features
- **Monitoring System**: Prometheus metrics
- **Health Checks**: Automatic monitoring
- **Secure Logging**: Sensitive data redaction
- **Error Handling**: No stack trace exposure
- **Background Tasks**: Automatic cleanup

### ✅ Quality Improvements
- Comprehensive test suite
- Dependency injection
- Connection pooling
- Graceful shutdown
- Log rotation

## Pre-Deployment Checklist

Run this first to check if everything is ready:

```batch
check-deployment-status.bat
```

## Manual Deployment (If Needed)

If you prefer to deploy step by step:

```batch
# 1. Run security fixes
deploy-security-fixes.bat

# 2. Test everything
python -m pytest tests\

# 3. Commit
git add -A
git commit -m "🔒 Apply security fixes"

# 4. Push
git push origin main
```

## After Deployment

1. **Check CI Status**: https://github.com/Breuk-AI/wordpress-mcp/actions
2. **Update .env file** with your WordPress credentials:
   ```
   WP_SITE_URL=https://your-site.com
   WP_USERNAME=your-username
   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
   ```

3. **Test the connection**:
   ```batch
   cd mcp-server
   python test_connection.py
   ```

## Rollback (If Needed)

If something goes wrong, backups are in:
```
backups\mcp-server_[timestamp]
backups\wp-mcp-plugin_[timestamp]
```

To rollback:
```batch
xcopy /E /I /Y backups\mcp-server_[timestamp] mcp-server
xcopy /E /I /Y backups\wp-mcp-plugin_[timestamp] wp-mcp-plugin
```

## Production Deployment

Once GitHub CI is green:

1. **Install on WordPress**:
   - Upload `wp-mcp-plugin` folder to `/wp-content/plugins/`
   - Activate in WordPress admin
   - Configure Application Password

2. **Deploy MCP Server**:
   ```bash
   # On your server
   git clone https://github.com/Breuk-AI/wordpress-mcp.git
   cd wordpress-mcp/mcp-server
   pip install -r requirements.txt
   python server.py
   ```

3. **Monitor Health**:
   - Check `/health` endpoint
   - View metrics at `/metrics`
   - Monitor logs in `logs/wordpress_mcp.log`

## Security Verification

After deployment, verify security:

```python
# Test path traversal protection
curl -X POST https://your-server/api/templates/read \
  -d '{"path": "../../../etc/passwd"}'
# Should return: 403 Forbidden

# Test rate limiting
for i in {1..100}; do
  curl https://your-server/api/posts
done
# Should get rate limited after 60 requests
```

## Support

- **CI Issues**: Check `.github/workflows/ci.yml`
- **Security Questions**: See `SECURITY_FIXES.md`
- **Deployment Problems**: Check `logs/deployment.log`

---

**Everything is automated and ready. Just run `ONE_CLICK_DEPLOY.bat` and focus on your race event! 🏁**

The deployment will:
- Take ~5 minutes
- Create automatic backups
- Push to GitHub with proper commit messages
- Get your green CI checkmark

Good luck with the race event! The WordPress MCP will be production-ready when you get back! 🎉
