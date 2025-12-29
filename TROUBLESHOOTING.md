# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Issue: `ModuleNotFoundError: No module named 'feedparser'`
**Solution:**
```bash
pip install -r requirements.txt
```
If using a virtual environment, make sure it's activated first.

#### Issue: `pip: command not found`
**Solution:**
Try using `pip3` instead:
```bash
pip3 install -r requirements.txt
```

#### Issue: Permission denied during installation
**Solution:**
Use `--user` flag:
```bash
pip install --user -r requirements.txt
```

---

### Authentication Issues

#### Issue: `credentials.json not found`
**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable Google Docs API
4. Create OAuth credentials (Desktop app type)
5. Download and save as `credentials.json` in project root

#### Issue: `invalid_grant` error during authentication
**Solution:**
Delete the token and re-authenticate:
```bash
rm token.pickle
python main.py --mode once
```

#### Issue: Browser doesn't open for authentication
**Solution:**
The script will print a URL. Copy and paste it into your browser manually.

#### Issue: `redirect_uri_mismatch` error
**Solution:**
Make sure you selected "Desktop app" (not "Web application") when creating OAuth credentials.

---

### Scraping Issues

#### Issue: No articles found
**Possible causes and solutions:**

1. **Keywords too specific**
   - Broaden your keyword list in `config.py`
   - Check spelling and variations
   - Add translated keywords for different languages

2. **RSS feeds not working**
   - Test feeds in browser to verify they work
   - Check logs for specific feed errors
   - Try alternative RSS feed URLs

3. **Recent news only**
   - RSS feeds typically show recent articles (24-48 hours)
   - Run the scraper more frequently to catch articles

**Debug:**
```bash
python test_scraper.py
```
This shows which keywords matched and in which articles.

#### Issue: Network errors (`No address associated with hostname`)
**Solution:**
- Check your internet connection
- Some networks block RSS feeds - try different network
- VPN might be blocking access
- Firewall settings

#### Issue: Feed parsing warnings
**Solution:**
These are usually harmless warnings. The scraper continues with other feeds.
Common causes:
- Malformed RSS XML
- Network timeout
- Server temporarily unavailable

---

### Google Docs Issues

#### Issue: "Access denied" when writing to document
**Solution:**
1. Make sure you're authenticated with correct Google account
2. If using existing doc ID, ensure you have edit access
3. Try creating a new document by leaving `GOOGLE_DOC_ID` empty

#### Issue: Document formatting looks wrong
**Solution:**
Google Docs API has limitations. The current implementation uses plain text formatting which is most reliable.

#### Issue: "Quota exceeded" error
**Solution:**
Google Docs API has rate limits:
- 300 requests per minute per user
- 600 requests per minute per project

If hitting limits:
- Reduce scraping frequency
- Reduce number of RSS feeds
- Wait and try again later

---

### Scheduling Issues

#### Issue: Schedule mode exits immediately
**Solution:**
Check for errors in the first run. The script will exit if scraping fails.
Run with `--mode once` first to debug.

#### Issue: Not running at expected intervals
**Solution:**
The scheduler checks every minute. Actual run times may vary by up to 1 minute.
For exact timing, use cron jobs instead.

#### Issue: Process killed after closing terminal
**Solution:**
Use one of these methods:
```bash
# nohup
nohup python main.py --mode schedule &

# screen
screen -S scraper
python main.py --mode schedule
# Ctrl+A, D to detach

# systemd service (recommended)
# See README.md for service file
```

---

### GitHub Actions Issues

#### Issue: Workflow not running on schedule
**Solution:**
- GitHub Actions schedules can be delayed by up to 10-15 minutes
- For inactive repos, scheduled workflows may be disabled
- Push a commit to re-activate

#### Issue: `GOOGLE_CREDENTIALS secret not found`
**Solution:**
1. Go to repository Settings → Secrets → Actions
2. Add new secret named `GOOGLE_CREDENTIALS`
3. Paste entire contents of `credentials.json`

#### Issue: Authentication fails in GitHub Actions
**Solution:**
GitHub Actions doesn't support interactive OAuth flow. You need to:
1. Run locally first to generate `token.pickle`
2. Convert `token.pickle` to JSON format
3. Store as GitHub Secret

Or use Service Account authentication instead of OAuth.

---

### Performance Issues

#### Issue: Scraping takes too long
**Solutions:**
- Reduce number of RSS feeds in `config.py`
- Reduce `MAX_ARTICLES_PER_RUN`
- Check for slow/unresponsive feeds in logs
- Remove problematic feeds

#### Issue: High memory usage
**Solutions:**
- Reduce `MAX_ARTICLES_PER_RUN`
- Restart periodically to clear `seen_urls` cache
- Process feeds in smaller batches

---

### Debugging Tips

1. **Enable verbose logging:**
```python
# In your script, before running
logging.basicConfig(level=logging.DEBUG)
```

2. **Check log file:**
```bash
tail -f scraper.log
```

3. **Test individual components:**
```bash
# Test scraper without Google Docs
python test_scraper.py

# Test with mocks
python test_unit.py
```

4. **Verify configuration:**
```python
import config
print(f"Keywords: {config.KEYWORDS}")
print(f"Feeds: {sum(len(f) for f in config.RSS_FEEDS.values())}")
```

5. **Test single feed:**
Temporarily modify `config.py` to have just one feed for testing.

---

### Getting Help

If you're still stuck:

1. Check `scraper.log` for error details
2. Run tests: `python test_unit.py`
3. Search existing GitHub issues
4. Create a new issue with:
   - Error message and full stack trace
   - Contents of `scraper.log`
   - Your configuration (without sensitive data)
   - Steps to reproduce

---

## Additional Resources

- [feedparser documentation](https://feedparser.readthedocs.io/)
- [Google Docs API documentation](https://developers.google.com/docs/api)
- [schedule library documentation](https://schedule.readthedocs.io/)
- [Python logging documentation](https://docs.python.org/3/library/logging.html)
