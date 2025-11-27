# Resources - Reaper Standalone Hacking Language

**Last Updated**: 2025-10-29

## Dependencies & Libraries

### Core Dependencies
- Python 3.8+ (existing interpreter)
- Existing Reaper codebase (lexer, parser, interpreter, etc.)

### Security Library Dependencies
- **Phantom (Network)**: Scapy, socket, threading
- **Crypt (Crypto)**: PyCryptodome, cryptography, PIL/Pillow
- **Wraith (System)**: os, sys, ctypes, psutil
- **Specter (Web)**: requests, beautifulsoup4, selenium/playwright
- **Shadow (Anonymity)**: stem (Tor), openvpn-python, netifaces

### Compilation Dependencies
- **Nuitka**: For Python-to-binary compilation
- **PyInstaller**: Alternative compilation option
- **Cross-compilation tools**: For Windows/Linux/macOS builds

### Development Tools
- pytest: Testing framework
- black: Code formatting
- flake8: Linting
- mypy: Type checking
- sphinx: Documentation generation

## Documentation References

### Language Design
- REAPER_AI_PROOF_PLAN.md: Complete implementation plan
- interpreter/language_spec.md: Current language specification
- interpreter/grammar.md: Formal grammar definition
- interpreter/README.md: Current features and usage

### Security References
- OWASP Top 10: Web security vulnerabilities
- NIST Cybersecurity Framework: Security best practices
- RFC documents: Network protocol specifications
- Cryptography standards: AES, RSA, SHA specifications

### Compilation References
- Nuitka documentation: Compilation options and configuration
- Python bytecode: Understanding Python VM
- Cross-platform compilation: Windows/Linux/macOS considerations

## Tools & Software

### Development Environment
- Python virtual environment
- Git for version control
- IDE: VSCode with Python extensions
- Terminal: PowerShell (Windows)

### Testing Tools
- pytest: Unit testing
- Coverage.py: Code coverage
- Fuzzing tools: For security testing
- Performance profilers: For optimization

### Distribution Tools
- GitHub: Source control and releases
- Docker: Containerization
- CI/CD: Automated testing and building

## External Resources

### Security Libraries
- Scapy: Packet manipulation
- Cryptography: Modern crypto algorithms
- Requests: HTTP client library
- BeautifulSoup: HTML parsing
- Selenium: Browser automation

### Learning Resources
- Python documentation: Language reference
- Security tutorials: Ethical hacking guides
- Compilation guides: Python-to-binary conversion
- Cross-platform development: Multi-OS considerations

## Notes
- All dependencies should be pinned to specific versions
- Security libraries require careful review for vulnerabilities
- Compilation dependencies may vary by platform
- Keep this file updated as new dependencies are added
