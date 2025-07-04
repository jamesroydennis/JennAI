# JennAI Architectural Blueprint
*Created by: Architect Persona*  
*Date: 2025-07-02*  
*Based on: Brand assets from src/presentation/brand/ and notebook instructions*

## 1. Executive Summary

This blueprint defines the foundational architecture for JennAI's presentation layer, synthesizing brand identity, thematic elements, and technical requirements into a cohesive implementation plan.

**Core Mission:** To bridge the unyielding question.

**Vision:** Illuminating the shared blindness through symbiotic AI-human collaboration.

## 2. Brand Asset Analysis

### 2.1 Visual Identity
- **Primary Logo:** `jennai-logo.png` - The foundational brand identifier
- **Favicon Assets:** Complete favicon set in `jennai-favicon_io/`
- **Background Assets:**
  - `background.jpg` & `background-light.jpg` - Primary backgrounds
  - `circuit-dark.jpg` & `circuit-light.jpg` - Technical/AI themed backgrounds
  - `heart-blackbackground.jpg` & `heart-blueforeground.jpg` - Emotional connection assets

### 2.2 Brand Content
- **Mission:** "To bridge the unyielding question."
- **Vision:** Focuses on illuminating shared blindness and AI evolution
- **Problem Statement:** Addresses dimensional blindness and communication gaps
- **Theme:** Technical sophistication balanced with human-centered design

### 2.3 Brand Theme SCSS
Primary theme colors and typography defined in `theme.scss`:
- Font System: Inter (headings) + Open Sans (body)
- Color Palette: Sky blue (#87CEEB), Dark cyan (#008B8B), Coral red (#FF6F61)

## 3. Technical Architecture

### 3.1 Framework Decision
**Primary:** Flask-based web application
**Rationale:** Matches existing project structure and Python ecosystem

### 3.2 Directory Structure Blueprint
```
src/presentation/api_server/flask_app/
├── app.py                    # Main Flask application entry
├── static/
│   ├── css/
│   │   ├── main.css         # Compiled from brand theme.scss
│   │   └── theme.scss       # Source SCSS (copied from brand)
│   ├── js/
│   │   └── scripts.js       # Core JavaScript functionality
│   └── img/                 # Brand assets (copied from brand dir)
│       ├── jennai-logo.png
│       ├── favicon.ico
│       └── [other brand images]
├── templates/
│   ├── base.html            # Base layout with brand integration
│   ├── index.html           # Homepage with mission/vision
│   └── error_templates/     # Error pages (from brand)
└── routes/
    └── main_routes.py       # Flask routing logic
```

### 3.3 Brand Content Integration
- Mission content loaded from `src/presentation/brand/mission.txt`
- Vision content loaded from `src/presentation/brand/vision.md`
- Problem statement from `src/presentation/brand/problem_statement.md`
- Dynamic content injection into templates

## 4. Implementation Requirements

### 4.1 Brand Asset Pipeline
1. Copy brand assets from `src/presentation/brand/` to Flask static directories
2. Compile `theme.scss` to `main.css` using SCSS compiler
3. Integrate favicon assets for browser compatibility
4. Ensure image optimization for web delivery

### 4.2 Template System
1. Base template with brand-consistent header/footer
2. Homepage template featuring mission, vision, and problem
3. Error templates using brand styling
4. Responsive design following brand guidelines

### 4.3 Flask Application Architecture
1. Main application entry point with brand content loading
2. Blueprint-based routing for scalability
3. Static asset serving with proper MIME types
4. Development and production configurations

## 5. Persona Handoff Requirements

### 5.1 For Contractor
- This blueprint defines WHAT to build
- Contractor must validate feasibility and create contracts
- Contractor decides which presentation platform to prioritize
- Contractor ensures brand compilation meets standards

### 5.2 For Constructor
- Detailed implementation specifications provided
- Clear directory structure and file requirements
- Brand asset integration workflows defined
- Testing requirements for each component

### 5.3 For Designer
- Brand application guidelines established
- SCSS compilation requirements specified
- Visual consistency standards defined
- Asset optimization parameters set

### 5.4 For Observer
- Success criteria for blueprint adherence
- Brand compliance checkpoints
- Quality gates for each implementation phase
- Final approval requirements

## 6. Success Criteria

### 6.1 Technical Validation
- [ ] Flask application starts without errors
- [ ] All brand assets properly served
- [ ] SCSS compiles to valid CSS
- [ ] Templates render with brand content
- [ ] Responsive design functions correctly

### 6.2 Brand Validation
- [ ] Mission/vision accurately displayed
- [ ] Brand colors and fonts applied consistently
- [ ] Logo and favicon properly integrated
- [ ] Visual hierarchy matches brand guidelines
- [ ] Content messaging aligned with brand voice

### 6.3 Architecture Validation
- [ ] Directory structure follows blueprint
- [ ] Separation of concerns maintained
- [ ] Scalable for future enhancements
- [ ] Compatible with existing project structure
- [ ] Documentation supports handoff to other personas

## 7. Risk Assessment

### 7.1 Technical Risks
- SCSS compilation dependencies
- Flask configuration complexity
- Asset optimization requirements
- Cross-browser compatibility

### 7.2 Brand Risks
- Content misalignment with vision
- Visual inconsistency across components
- Mission messaging dilution
- Brand asset quality degradation

### 7.3 Mitigation Strategies
- Comprehensive testing at each phase
- Regular brand compliance reviews
- Version control for all assets
- Clear documentation for each persona

## 8. Next Steps

1. **Contractor Review:** Validate technical feasibility and create implementation contracts
2. **Asset Preparation:** Organize brand assets for distribution
3. **Development Environment:** Ensure all dependencies available
4. **Implementation Kickoff:** Hand off to Constructor with detailed specifications

---

*This blueprint serves as the foundational document for all subsequent persona work. Any deviations must be approved through proper architectural review process.*

**Architect Signature:** ✓ Blueprint Approved  
**Handoff Status:** Ready for Contractor Review
