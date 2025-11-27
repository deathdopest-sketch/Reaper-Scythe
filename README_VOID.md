# Void OSINT Scrubbing Library

The **Void** library provides comprehensive tools for removing digital footprints, scrubbing OSINT data, and protecting privacy by minimizing online exposure.

## Features

### Core Scrubbing Operations

- **Email Scrubbing**: Remove email addresses from data brokers and public databases
- **Phone Number Scrubbing**: Remove phone numbers from public directories
- **Username Checking**: Check username availability and remove accounts across platforms
- **Domain Cleanup**: Remove domain information from public sources
- **Social Media Scanning**: Scan for accounts across major platforms

### Digital Footprint Analysis

- **Comprehensive Analysis**: Analyze digital footprints across multiple sources
- **Exposure Detection**: Find exposed emails, phones, and personal information
- **Severity Assessment**: Categorize findings by severity level
- **Report Generation**: Generate detailed footprint reports

### Removal Request Management

- **Multi-Provider Support**: Submit removal requests to Google, Bing, data brokers
- **Status Tracking**: Track removal request status over time
- **Automated Follow-ups**: Manage and follow up on deletion requests
- **Provider Integration**: Support for major data brokers and platforms

## Usage Examples

### Basic Email Scrubbing

```python
from libs.void import scrub_email

# Scrub email from public sources (safe mode - read only)
result = scrub_email("user@example.com", safe_mode=True)

print(f"Status: {result.status}")
print(f"Platforms checked: {len(result.platforms_checked)}")
print(f"Items removed: {result.items_removed}")
```

### Phone Number Scrubbing

```python
from libs.void import scrub_phone

result = scrub_phone("+1-555-123-4567", safe_mode=True)
print(f"Success rate: {result.success_rate():.1f}%")
```

### Username Checking

```python
from libs.void import check_username_availability

# Check if username is available across platforms
availability = check_username_availability("testuser")

for platform, is_taken in availability.items():
    status = "TAKEN" if is_taken else "AVAILABLE"
    print(f"{platform}: {status}")
```

### Digital Footprint Analysis

```python
from libs.void import analyze_digital_footprint

# Analyze comprehensive digital footprint
report = analyze_digital_footprint(
    email="user@example.com",
    username="testuser",
    phone="+1-555-123-4567"
)

print(f"Total records: {report['total_records']}")
print(f"Critical records: {report['critical_count']}")
print(f"Removable: {report['removable_count']}")
```

### Removal Requests

```python
from libs.void import request_google_removal, request_data_broker_removal

# Request Google search result removal
google_request = request_google_removal("https://example.com/remove-this")
print(f"Request ID: {google_request.request_id}")

# Request data broker removal
broker_request = request_data_broker_removal(
    "whitepages",
    "user@example.com",
    "email"
)
```

## Safe Mode

All operations default to **safe mode**, which:
- Performs read-only checks
- Does not make actual deletions
- Shows what would be removed
- Provides detailed reports

To perform actual removals, set `safe_mode=False`:

```python
from libs.void import VoidOSINTScrubber

scrubber = VoidOSINTScrubber(safe_mode=False)
result = scrubber.scrub_email("user@example.com")
```

⚠️ **Warning**: Actual removal operations may have legal and ethical implications. Use responsibly.

## Supported Platforms

### Data Brokers
- WhitePages
- Spokeo
- BeenVerified
- PeopleFinder
- Intelius
- Pipl
- TruePeopleSearch
- FastPeopleSearch

### Social Media Platforms
- Facebook
- Twitter/X
- Instagram
- LinkedIn
- GitHub
- Reddit
- TikTok
- Snapchat
- Pinterest
- YouTube

### Search Engines
- Google (removal requests)
- Bing (removal requests)
- Yahoo
- DuckDuckGo

## Security Features

- **Email Validation**: Proper email format checking
- **Phone Normalization**: Standardized phone number handling
- **Privacy Protection**: Safe mode prevents accidental deletions
- **Audit Trail**: Complete history of scrubbing operations
- **Status Tracking**: Monitor removal request progress

## Integration with Reaper Language

The Void library integrates seamlessly with the Reaper language:

```reaper
// Import the void library
infiltrate void;

// Scrub email address
corpse email_result = void.scrub_email("user@example.com", true);

// Analyze digital footprint
crypt footprint = void.analyze_footprint("user@example.com", "testuser");
```

## Legal and Ethical Considerations

⚠️ **Important**: 

- Only use this library for legitimate privacy protection purposes
- Respect platform terms of service
- Obtain proper authorization before removing others' information
- Follow local laws and regulations
- Use safe mode for testing and analysis

## Documentation

For complete API documentation, see the Void library reference guide.

## Contributing

The Void library is part of the Reaper Security Language project. Contributions are welcome for:
- Additional platform support
- Improved removal automation
- Enhanced footprint analysis
- Better status tracking

## License

Part of the Reaper Security Language project - see main project license.

