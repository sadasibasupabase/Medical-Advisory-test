// Medical Research Portal JavaScript

class ResearchPortal {
    constructor() {
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Research query form
        const queryForm = document.getElementById('researchQueryForm');
        if (queryForm) {
            queryForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitResearchQuery();
            });
        }
        
        // Paper upload form
        const uploadForm = document.getElementById('uploadPaperForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.uploadPaper();
            });
        }
    }
    
    async submitResearchQuery() {
        const query = document.getElementById('researchQuery').value.trim();
        const model = document.getElementById('queryModel').value;
        
        if (!query) {
            alert('Please enter a research question');
            return;
        }
        
        const submitBtn = document.querySelector('#researchQueryForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Set loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Analyzing...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/research_query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    model: model
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                this.displayQueryResults(data.response, data.papers_count);
            }
            
        } catch (error) {
            console.error('Research query error:', error);
            alert('Failed to process research query. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    displayQueryResults(response, papersCount) {
        const resultsDiv = document.getElementById('queryResults');
        const contentDiv = document.getElementById('queryResultContent');
        
        // Format the response for better display
        let formattedResponse = this.formatResearchResponse(response);
        
        contentDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6 class="mb-0">Analysis Results</h6>
                <span class="badge bg-info">${papersCount} papers analyzed</span>
            </div>
            ${formattedResponse}
        `;
        
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    formatResearchResponse(response) {
        let formatted = this.escapeHtml(response);
        
        // Convert line breaks to HTML
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Format bold sections
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format evidence tables
        formatted = formatted.replace(/\*\*Study:\*\* (.*?)<br>/g, '<div class="evidence-study mt-3 p-3 bg-light rounded"><h6 class="text-primary">📋 $1</h6>');
        formatted = formatted.replace(/---<br>/g, '</div>');
        
        // Format list items
        formatted = formatted.replace(/- \*\*(.*?)\*\* (.*?)<br>/g, '<div class="mb-1"><strong>$1:</strong> $2</div>');
        
        // Format sections
        formatted = formatted.replace(/\*\*(Research Summary|Clinical Implications|Limitations):\*\* (.*?)(<br><br>|$)/g, 
            '<div class="mt-3"><h6 class="text-success">$1:</h6><p>$2</p></div>');
        
        // Add medical disclaimer styling
        formatted = formatted.replace(
            /\*\*IMPORTANT MEDICAL DISCLAIMER:\*\*(.*?)(?=<br><br>|$)/gi,
            '<div class="alert alert-warning mt-3"><i class="fas fa-exclamation-triangle me-2"></i><strong>IMPORTANT MEDICAL DISCLAIMER:</strong>$1</div>'
        );
        
        return formatted;
    }
    
    async uploadPaper() {
        const title = document.getElementById('paperTitle').value.trim();
        const content = document.getElementById('paperContent').value.trim();
        
        if (!title || !content) {
            alert('Please fill in both title and content');
            return;
        }
        
        if (content.length < 100) {
            alert('Paper content seems too short. Please provide the full research paper text.');
            return;
        }
        
        const submitBtn = document.querySelector('#uploadPaperForm button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Set loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Uploading...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/api/upload_paper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                alert('Error: ' + data.error);
            } else {
                alert('Paper uploaded successfully!');
                
                // Clear form
                document.getElementById('paperTitle').value = '';
                document.getElementById('paperContent').value = '';
                
                // Switch to library tab to show uploaded papers
                document.getElementById('library-tab').click();
                
                // Reload page to show new paper
                setTimeout(() => location.reload(), 1000);
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload paper. Please try again.');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for template usage
function setResearchQuery(query) {
    const queryInput = document.getElementById('researchQuery');
    if (queryInput) {
        queryInput.value = query;
        queryInput.focus();
        
        // Switch to query tab if not already active
        document.getElementById('query-tab').click();
    }
}

function viewPaper(paperId) {
    // In a real implementation, this would fetch the paper details
    // For now, show a placeholder modal
    const modal = new bootstrap.Modal(document.createElement('div'));
    modal._element.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Research Paper Viewer</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="text-center py-5">
                        <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                        <h6>Paper ID: ${paperId}</h6>
                        <p class="text-muted">
                            Paper viewing functionality would be implemented here.<br>
                            This would show the full text of the research paper with highlighting and search capabilities.
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary">
                        <i class="fas fa-download me-1"></i>Download
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal._element);
    modal.show();
    
    // Clean up modal after hiding
    modal._element.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal._element);
    });
}

// Initialize research portal when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.researchPortal = new ResearchPortal();
    
    // Auto-resize textarea for paper content
    const paperContent = document.getElementById('paperContent');
    if (paperContent) {
        paperContent.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
    
    // Add helpful tips
    addResearchTips();
});

function addResearchTips() {
    // Add contextual tips based on the active tab
    const queryTab = document.getElementById('query-tab');
    const uploadTab = document.getElementById('upload-tab');
    
    if (queryTab) {
        queryTab.addEventListener('click', () => {
            setTimeout(() => {
                const queryInput = document.getElementById('researchQuery');
                if (queryInput && !queryInput.value) {
                    queryInput.placeholder = 'e.g., "What are the most effective treatments for chronic pain in elderly patients?"';
                }
            }, 100);
        });
    }
    
    if (uploadTab) {
        uploadTab.addEventListener('click', () => {
            setTimeout(() => {
                const titleInput = document.getElementById('paperTitle');
                if (titleInput && !titleInput.value) {
                    titleInput.placeholder = 'e.g., "Efficacy of Novel Treatment X in Randomized Controlled Trial"';
                }
            }, 100);
        });
    }
}

// Keyboard shortcuts for research portal
document.addEventListener('keydown', function(e) {
    // Ctrl + Q for quick query focus
    if (e.ctrlKey && e.key === 'q') {
        e.preventDefault();
        document.getElementById('query-tab').click();
        setTimeout(() => {
            document.getElementById('researchQuery').focus();
        }, 100);
    }
    
    // Ctrl + U for upload focus
    if (e.ctrlKey && e.key === 'u') {
        e.preventDefault();
        document.getElementById('upload-tab').click();
        setTimeout(() => {
            document.getElementById('paperTitle').focus();
        }, 100);
    }
});

// Research paper validation
function validatePaperContent(content) {
    const minLength = 500;
    const requiredSections = ['abstract', 'introduction', 'method', 'result', 'conclusion'];
    
    if (content.length < minLength) {
        return {
            valid: false,
            message: `Paper content should be at least ${minLength} characters long for meaningful analysis.`
        };
    }
    
    const contentLower = content.toLowerCase();
    const foundSections = requiredSections.filter(section => 
        contentLower.includes(section) || contentLower.includes(section + 's')
    );
    
    if (foundSections.length < 2) {
        return {
            valid: false,
            message: 'Paper should include typical research sections like abstract, methods, results, etc. for better AI analysis.'
        };
    }
    
    return { valid: true };
}

// Enhanced upload with validation
function enhancedUploadPaper() {
    const content = document.getElementById('paperContent').value.trim();
    const validation = validatePaperContent(content);
    
    if (!validation.valid) {
        if (confirm(`${validation.message}\n\nDo you want to upload anyway?`)) {
            window.researchPortal.uploadPaper();
        }
    } else {
        window.researchPortal.uploadPaper();
    }
}
