# Google Sheets Integration - Feature Summary

## What Was Added

This update adds comprehensive Google Sheets integration to the RSS feed scraper, providing structured, spreadsheet-based output alongside the existing Google Docs support.

## Key Features

### 1. Structured Column Layout

Articles are now pushed to Google Sheets with the following columns:

| Column | Description |
|--------|-------------|
| **Timestamp** | When the article was scraped (YYYY-MM-DD HH:MM:SS) |
| **Title** | Article headline |
| **Link** | Full URL to the original article |
| **Summary** | Article excerpt/summary (max 500 characters) |
| **Source** | Name of the news source |
| **Language** | Language of the article (english/hindi/marathi) |
| **Published Date** | Original publication date from RSS feed |
| **Matched Keywords** | Comma-separated list of keywords that matched |

### 2. Auto-Formatting

- **Header Row**: Automatically formatted with bold text and gray background
- **Column Width**: Auto-resizes to fit content
- **Frozen Header**: First row is frozen for easy scrolling

### 3. Dual Output Support

You can now choose between two output formats:

#### Google Sheets (Default)
- Structured, tabular data
- Easy to sort, filter, and analyze
- Perfect for sharing with teams
- Can export to Excel/CSV

#### Google Docs
- Text-based format
- Narrative style
- Good for reading and reviewing

### 4. Flexible Configuration

**In `config.py`:**
```python
# Choose your preferred output format
OUTPUT_FORMAT = "sheets"  # or "docs"

# Target specific spreadsheet (optional)
GOOGLE_SHEET_ID = "your-spreadsheet-id"

# Or target specific document (optional)
GOOGLE_DOC_ID = "your-document-id"
```

**Command-line override:**
```bash
# Override to use sheets
python main.py --mode once --output sheets

# Override to use docs
python main.py --mode once --output docs
```

### 5. Append Mode

The scraper can append to an existing spreadsheet, allowing you to:
- Build a continuous log of articles over time
- Maintain a single spreadsheet for all updates
- Track articles across multiple scraping runs

**Usage:**
```bash
# Create new spreadsheet
python main.py --mode once

# Append to existing spreadsheet
python main.py --mode once --sheet-id YOUR_SPREADSHEET_ID
```

### 6. Matched Keywords Column

A unique feature that shows which keywords triggered each article:
- Helps understand why an article was captured
- Useful for refining keyword lists
- Enables filtering by specific keywords in the spreadsheet

## Usage Examples

### Basic Usage

```bash
# Run once with Google Sheets (default)
python main.py --mode once

# Run on schedule every hour
python main.py --mode schedule --interval 1
```

### Advanced Usage

```bash
# Append to specific spreadsheet
python main.py --mode once --sheet-id 1abc...xyz

# Switch to Google Docs
python main.py --mode once --output docs

# Run every 2 hours with sheets
python main.py --mode schedule --interval 2 --output sheets
```

### Testing

```bash
# Test Google Sheets integration (requires credentials)
python test_sheets.py

# Test scraping without Google APIs
python test_scraper.py

# Run unit tests
python test_unit.py
```

## Setup Instructions

### 1. Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Go to "APIs & Services" > "Library"
4. Search for "Google Sheets API"
5. Click "Enable"

### 2. Update Credentials

Your existing `credentials.json` will work if it has the Sheets scope. If you get authentication errors:
1. Delete `token.pickle`
2. Run the scraper again to re-authenticate
3. The new authentication will include Sheets permissions

### 3. Configure Output Format

Edit `config.py`:
```python
OUTPUT_FORMAT = "sheets"  # Default is now sheets
```

### 4. Run the Scraper

```bash
python main.py --mode once
```

On first run (or after re-authentication), your browser will open to grant permissions.

## GitHub Actions

The workflow has been updated to use Google Sheets by default:

**Required Secrets:**
- `GOOGLE_CREDENTIALS` - Contents of your credentials.json
- `GOOGLE_SHEET_ID` - Your target spreadsheet ID (optional)

**Manual trigger:**
1. Go to Actions tab in GitHub
2. Select "RSS Feed Scraper" workflow
3. Click "Run workflow"

## Example Output

### Google Sheets View

```
┌─────────────────────┬────────────────────────┬──────────────┬─────────────┬────────────┬──────────┬─────────────────┬──────────────────┐
│ Timestamp           │ Title                  │ Link         │ Summary     │ Source     │ Language │ Published Date  │ Matched Keywords │
├─────────────────────┼────────────────────────┼──────────────┼─────────────┼────────────┼──────────┼─────────────────┼──────────────────┤
│ 2025-12-29 16:35:00 │ AAP announces policy   │ https://...  │ The party...│ TOI Mumbai │ english  │ 2025-12-29T...  │ aap, party       │
│ 2025-12-29 16:35:00 │ भाजपा ने आरोप लगाए   │ https://...  │ भारतीय...  │ Dainik B.  │ hindi    │ 2025-12-29T...  │ भाजपा, aap       │
└─────────────────────┴────────────────────────┴──────────────┴─────────────┴────────────┴──────────┴─────────────────┴──────────────────┘
```

### Benefits

1. **Easy Analysis**: Use spreadsheet functions to analyze trends
2. **Filtering**: Filter by language, source, or matched keywords
3. **Sorting**: Sort by date, source, or any column
4. **Sharing**: Share spreadsheet link with team members
5. **Export**: Download as Excel or CSV for further processing
6. **History**: Build a continuous log of all articles over time

## Migration from Google Docs

If you were using Google Docs before:

1. Your existing setup continues to work
2. To switch to Sheets, change `OUTPUT_FORMAT = "sheets"` in config.py
3. Or use `--output sheets` command-line flag
4. Both outputs can coexist - use different commands for different needs

## Files Added/Modified

**New Files:**
- `google_sheets.py` - Google Sheets integration module
- `test_sheets.py` - Test script for Sheets integration
- `SHEETS_INTEGRATION.md` - This document

**Modified Files:**
- `main.py` - Added Sheets support and CLI options
- `config.py` - Added OUTPUT_FORMAT and GOOGLE_SHEET_ID
- `config.example.py` - Updated example configuration
- `google_docs.py` - Added Sheets scope for compatibility
- `README.md` - Updated with Sheets documentation
- `QUICKSTART.md` - Added Sheets examples
- `.github/workflows/scraper.yml` - Updated for Sheets output

## Support

For issues or questions about Google Sheets integration:
1. Check the TROUBLESHOOTING.md guide
2. Review example output in test_sheets.py
3. Create an issue on GitHub with details

## Summary

Google Sheets integration provides a powerful, structured way to track news articles with proper columns for all metadata. The spreadsheet format makes it easy to analyze trends, share with teams, and export data for further processing.
