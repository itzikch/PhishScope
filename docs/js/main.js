// PhishScope Website JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize syntax highlighting
    hljs.highlightAll();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Demo tabs functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const demoPanels = document.querySelectorAll('.demo-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            demoPanels.forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked button and corresponding panel
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
    
    // Navbar scroll effect
    let lastScroll = 0;
    const navbar = document.querySelector('.navbar');
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.boxShadow = 'none';
        }
        
        lastScroll = currentScroll;
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe feature cards, use cases, etc.
    document.querySelectorAll('.feature-card, .use-case, .doc-card, .contribute-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Terminal typing effect (optional enhancement)
    const terminalCode = document.querySelector('.terminal-body code');
    if (terminalCode) {
        const originalText = terminalCode.innerHTML;
        let index = 0;
        
        // Uncomment to enable typing effect
        /*
        terminalCode.innerHTML = '';
        
        function typeWriter() {
            if (index < originalText.length) {
                terminalCode.innerHTML += originalText.charAt(index);
                index++;
                setTimeout(typeWriter, 20);
            }
        }
        
        // Start typing effect after a delay
        setTimeout(typeWriter, 1000);
        */
    }
    
    // Copy code button functionality
    document.querySelectorAll('pre code').forEach(block => {
        const pre = block.parentElement;
        const button = document.createElement('button');
        button.className = 'copy-btn';
        button.innerHTML = '<i class="fas fa-copy"></i>';
        button.title = 'Copy code';
        
        button.addEventListener('click', function() {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(() => {
                button.innerHTML = '<i class="fas fa-check"></i>';
                button.style.color = '#10b981';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-copy"></i>';
                    button.style.color = '';
                }, 2000);
            });
        });
        
        pre.style.position = 'relative';
        pre.appendChild(button);
    });
    
    // Add copy button styles dynamically
    const style = document.createElement('style');
    style.textContent = `
        .copy-btn {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #6366f1;
            padding: 0.5rem;
            border-radius: 0.25rem;
            cursor: pointer;
            opacity: 0;
            transition: all 0.3s;
            font-size: 0.875rem;
        }
        
        pre:hover .copy-btn {
            opacity: 1;
        }
        
        .copy-btn:hover {
            background: rgba(99, 102, 241, 0.3);
        }
    `;
    document.head.appendChild(style);
    
    // Stats counter animation
    const stats = document.querySelectorAll('.stat-value');
    const statsObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const finalValue = target.textContent;
                
                // Only animate numbers
                if (!isNaN(parseInt(finalValue))) {
                    let current = 0;
                    const increment = parseInt(finalValue) / 50;
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= parseInt(finalValue)) {
                            target.textContent = finalValue;
                            clearInterval(timer);
                        } else {
                            target.textContent = Math.floor(current);
                        }
                    }, 30);
                }
                
                statsObserver.unobserve(target);
            }
        });
    }, { threshold: 0.5 });
    
    stats.forEach(stat => statsObserver.observe(stat));
    
    // Mobile menu toggle (if needed)
    const createMobileMenu = () => {
        const navMenu = document.querySelector('.nav-menu');
        const navbar = document.querySelector('.navbar .container');
        
        if (window.innerWidth <= 640 && !document.querySelector('.mobile-menu-btn')) {
            const menuBtn = document.createElement('button');
            menuBtn.className = 'mobile-menu-btn';
            menuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            menuBtn.style.cssText = `
                display: block;
                background: transparent;
    
    // ========================================
    // Live Simulator Functionality
    // ========================================
    
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const verboseMode = document.getElementById('verboseMode');
    const simulateMode = document.getElementById('simulateMode');
    const simulatorOutput = document.getElementById('simulatorOutput');
    const terminalOutput = document.getElementById('terminalOutput');
    const resultsPanel = document.getElementById('resultsPanel');
    const clearOutput = document.getElementById('clearOutput');
    
    // Sample phishing patterns for simulation
    const phishingPatterns = {
        'phish': { risk: 'high', forms: 1, jsPatterns: 5, exfil: 2 },
        'suspicious': { risk: 'medium', forms: 1, jsPatterns: 2, exfil: 1 },
        'secure': { risk: 'low', forms: 0, jsPatterns: 0, exfil: 0 },
        'login': { risk: 'medium', forms: 1, jsPatterns: 3, exfil: 1 },
        'verify': { risk: 'high', forms: 1, jsPatterns: 4, exfil: 2 },
        'account': { risk: 'medium', forms: 1, jsPatterns: 2, exfil: 1 }
    };
    
    if (analyzeBtn) {
        console.log('Analyze button found, attaching event listener');
        analyzeBtn.addEventListener('click', function() {
            console.log('Analyze button clicked');
            const url = urlInput.value.trim();
            console.log('URL entered:', url);
            
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                alert('Please enter a valid URL starting with http:// or https://');
                return;
            }
            
            console.log('Simulation mode:', simulateMode.checked);
            if (simulateMode.checked) {
                runSimulation(url);
            } else {
                alert('Real analysis mode is not available in the web interface. Please use the CLI tool:\n\npython phishscope.py analyze ' + url);
            }
        });
    } else {
        console.error('Analyze button not found! Check if element ID is correct.');
    }
    
    if (clearOutput) {
        clearOutput.addEventListener('click', function() {
            simulatorOutput.style.display = 'none';
            terminalOutput.innerHTML = '';
            resultsPanel.style.display = 'none';
        });
    }
    
    // Result tabs functionality
    document.querySelectorAll('.result-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const targetResult = this.getAttribute('data-result');
            
            document.querySelectorAll('.result-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.result-panel').forEach(p => p.classList.remove('active'));
            
            this.classList.add('active');
            document.getElementById(targetResult).classList.add('active');
        });
    });
    
    function runSimulation(url) {
        // Show output section
        simulatorOutput.style.display = 'block';
        terminalOutput.innerHTML = '';
        resultsPanel.style.display = 'none';
        
        // Disable button during analysis
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading"></span> Analyzing...';
        
        // Determine risk level based on URL keywords
        let riskData = { risk: 'low', forms: 0, jsPatterns: 0, exfil: 0 };
        const urlLower = url.toLowerCase();
        
        for (const [keyword, data] of Object.entries(phishingPatterns)) {
            if (urlLower.includes(keyword)) {
                riskData = data;
                break;
            }
        }
        
        // Simulate analysis steps
        const steps = [
            { delay: 500, text: `<span class="text-cyan">INFO:</span> Starting analysis of: ${url}`, color: 'cyan' },
            { delay: 1000, text: `<span class="text-green">✓</span> [1/5] Loading page...`, color: 'green' },
            { delay: 1500, text: `<span class="text-green">✓</span> [2/5] Inspecting DOM...`, color: 'green' },
            { delay: 2000, text: `<span class="text-green">✓</span> [3/5] Analyzing JavaScript...`, color: 'green' },
            { delay: 2500, text: `<span class="text-green">✓</span> [4/5] Analyzing network traffic...`, color: 'green' },
            { delay: 3000, text: `<span class="text-green">✓</span> [5/5] Generating report...`, color: 'green' },
            { delay: 3500, text: '', color: 'none' },
            { delay: 3600, text: `<span class="text-cyan">📊 Quick Summary:</span>`, color: 'cyan' },
            { delay: 3700, text: `  • Forms detected: <span class="text-yellow">${riskData.forms}</span>`, color: 'white' },
            { delay: 3800, text: `  • Suspicious JS patterns: <span class="${riskData.jsPatterns > 2 ? 'text-red' : 'text-yellow'}">${riskData.jsPatterns}</span>`, color: 'white' },
            { delay: 3900, text: `  • Exfiltration endpoints: <span class="${riskData.exfil > 0 ? 'text-red' : 'text-green'}">${riskData.exfil}</span>`, color: 'white' },
            { delay: 4000, text: '', color: 'none' },
            { delay: 4100, text: `<span class="text-green">✅ Analysis complete!</span>`, color: 'green' }
        ];
        
        let currentStep = 0;
        
        function displayNextStep() {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                setTimeout(() => {
                    const line = document.createElement('div');
                    line.innerHTML = step.text;
                    terminalOutput.appendChild(line);
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                    currentStep++;
                    displayNextStep();
                }, step.delay - (currentStep > 0 ? steps[currentStep - 1].delay : 0));
            } else {
                // Analysis complete, show results
                setTimeout(() => {
                    showResults(url, riskData);
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze URL';
                }, 500);
            }
        }
        
        displayNextStep();
    }
    
    function showResults(url, riskData) {
        resultsPanel.style.display = 'block';
        
        // Generate summary
        const summaryPanel = document.getElementById('summary');
        const riskLevel = riskData.risk.toUpperCase();
        const riskClass = riskData.risk;
        
        let confidence = 'LOW';
        let confidenceText = 'Limited phishing indicators detected.';
        
        if (riskData.risk === 'high') {
            confidence = 'HIGH';
            confidenceText = 'Multiple phishing indicators detected. This appears to be a phishing attack.';
        } else if (riskData.risk === 'medium') {
            confidence = 'MEDIUM';
            confidenceText = 'Some suspicious characteristics detected. Further investigation recommended.';
        }
        
        summaryPanel.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-chart-bar"></i> Analysis Summary</h4>
                <p><strong>URL:</strong> <code>${url}</code></p>
                <p><strong>Confidence Level:</strong> <span class="result-badge ${riskClass}">${confidence}</span></p>
                <p>${confidenceText}</p>
            </div>
            <div class="result-card">
                <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                <ul class="result-list">
                    <li>
                        <span>Forms Detected</span>
                        <span class="result-badge ${riskData.forms > 0 ? 'medium' : 'info'}">${riskData.forms}</span>
                    </li>
                    <li>
                        <span>Suspicious JavaScript Patterns</span>
                        <span class="result-badge ${riskData.jsPatterns > 2 ? 'high' : riskData.jsPatterns > 0 ? 'medium' : 'info'}">${riskData.jsPatterns}</span>
                    </li>
                    <li>
                        <span>Exfiltration Endpoints</span>
                        <span class="result-badge ${riskData.exfil > 0 ? 'high' : 'info'}">${riskData.exfil}</span>
                    </li>
                </ul>
            </div>
        `;
        
        // Generate DOM analysis
        const domPanel = document.getElementById('dom');
        domPanel.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-code"></i> DOM Structure Analysis</h4>
                <p><strong>Forms Detected:</strong> ${riskData.forms}</p>
                ${riskData.forms > 0 ? `
                    <p>Found ${riskData.forms} form(s) with password fields. Form submission may be intercepted by JavaScript.</p>
                    <ul class="result-list">
                        <li><span>Password Fields</span><span class="result-badge medium">1</span></li>
                        <li><span>Hidden Inputs</span><span class="result-badge info">${Math.floor(Math.random() * 3) + 1}</span></li>
                        <li><span>Form Action</span><span>JavaScript-based</span></li>
                    </ul>
                ` : '<p>No forms detected on this page.</p>'}
            </div>
        `;
        
        // Generate JavaScript analysis
        const jsPanel = document.getElementById('javascript');
        jsPanel.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-file-code"></i> JavaScript Behavior</h4>
                <p><strong>Suspicious Patterns:</strong> ${riskData.jsPatterns}</p>
                ${riskData.jsPatterns > 0 ? `
                    <ul class="result-list">
                        <li><span>Input Event Listeners</span><span class="result-badge ${riskData.jsPatterns > 3 ? 'high' : 'medium'}">Detected</span></li>
                        <li><span>Password Field Access</span><span class="result-badge ${riskData.jsPatterns > 2 ? 'high' : 'medium'}">Detected</span></li>
                        <li><span>Fetch/XHR POST Requests</span><span class="result-badge ${riskData.jsPatterns > 1 ? 'medium' : 'info'}">Detected</span></li>
                        <li><span>JSON Serialization</span><span class="result-badge info">Detected</span></li>
                    </ul>
                    <p style="margin-top: 1rem; color: var(--text-secondary);">
                        <i class="fas fa-info-circle"></i> JavaScript code appears to monitor user input and may exfiltrate credentials.
                    </p>
                ` : '<p>No suspicious JavaScript patterns detected.</p>'}
            </div>
        `;
        
        // Generate network analysis
        const networkPanel = document.getElementById('network');
        networkPanel.innerHTML = `
            <div class="result-card">
                <h4><i class="fas fa-network-wired"></i> Network Traffic</h4>
                <p><strong>Exfiltration Candidates:</strong> ${riskData.exfil}</p>
                ${riskData.exfil > 0 ? `
                    <div style="margin-top: 1rem;">
                        <p><strong>Suspicious Endpoint Detected:</strong></p>
                        <code style="display: block; background: var(--code-bg); padding: 1rem; border-radius: 0.25rem; margin: 0.5rem 0;">
                            POST https://api.phish-collector.tk/collect/credentials
                        </code>
                        <ul class="result-list" style="margin-top: 1rem;">
                            <li><span>Suspicious TLD (.tk)</span><span class="result-badge high">HIGH RISK</span></li>
                            <li><span>Data-related URL</span><span class="result-badge medium">SUSPICIOUS</span></li>
                            <li><span>POST Method</span><span class="result-badge medium">SUSPICIOUS</span></li>
                        </ul>
                    </div>
                ` : '<p>No suspicious network activity detected.</p>'}
            </div>
        `;
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
                border: none;
                color: var(--text-primary);
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0.5rem;
            `;
            
            menuBtn.addEventListener('click', () => {
                navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
                navMenu.style.flexDirection = 'column';
                navMenu.style.position = 'absolute';
                navMenu.style.top = '100%';
                navMenu.style.left = '0';
                navMenu.style.right = '0';
                navMenu.style.background = 'var(--dark-bg)';
                navMenu.style.padding = '1rem';
                navMenu.style.borderTop = '1px solid var(--border-color)';
            });
            
            navbar.appendChild(menuBtn);
        }
    };
    
    createMobileMenu();
    window.addEventListener('resize', createMobileMenu);
    
    console.log('🔍 PhishScope website loaded successfully!');
});

// Made with Bob
