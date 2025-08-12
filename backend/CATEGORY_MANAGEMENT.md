# Category and Subcategory Management Guide

This guide explains how to manage categories and subcategories for projects and services in the portfolio application.

## Overview

The portfolio application now supports both categories and subcategories for:
- **Projects**: 8 main categories with multiple subcategories each
- **Services**: 4 main categories with multiple subcategories each

## File Structure

### Main Files
- `portfolio/constants.py` - Central location for all categories and subcategories
- `portfolio/models.py` - Updated models with subcategory fields
- `portfolio/admin.py` - Enhanced admin interface with filtering
- `portfolio/views.py` - API endpoints with category/subcategory support

### Static Files
- `portfolio/static/admin/js/category_subcategory.js` - Dynamic subcategory selection in admin

## Project Categories

### Residential
- Single Family Home
- Multi Family Home
- Apartment Complex
- Townhouse
- Villa
- Penthouse
- Studio Apartment

### Commercial
- Office Building
- Shopping Mall
- Restaurant
- Hotel
- Retail Store
- Warehouse
- Showroom
- Clinic
- Bank

### Public
- School
- University
- Hospital
- Museum
- Library
- Government Building
- Community Center
- Religious Building
- Transportation Hub

### Industrial
- Manufacturing Plant
- Power Plant
- Chemical Plant
- Food Processing
- Automotive Plant
- Steel Mill
- Oil Refinery
- Research Facility

### Landscape
- Public Garden
- Private Garden
- Urban Plaza
- Playground
- Sports Complex
- Park
- Golf Course
- Cemetery

### Interior
- Living Room
- Kitchen
- Bedroom
- Bathroom
- Office Space
- Restaurant Interior
- Hotel Room
- Reception Area

### Urban
- Master Planning
- Mixed Use Development
- Transit Oriented
- Waterfront Development
- Historic District
- Smart City
- Sustainable Community
- Urban Renewal

### Other
- Custom Design
- Prototype
- Renovation
- Restoration
- Conceptual
- Competition Entry

## Service Categories

### Design
- Architectural Design
- Interior Design
- Landscape Design
- Urban Planning
- Structural Design
- MEP Design
- Facade Design

### Planning
- Site Planning
- Master Planning
- Zoning Analysis
- Feasibility Study
- Environmental Planning
- Traffic Planning
- Infrastructure Planning

### Consulting
- Design Consultation
- Project Management
- Construction Administration
- Code Compliance
- Sustainability Consulting
- Cost Estimation
- Risk Assessment

### Visualization
- 3D Rendering
- Animation
- Virtual Reality
- Architectural Photography
- Presentation Design
- Technical Drawing
- Model Making

## How to Add/Remove Categories and Subcategories

### 1. Edit Constants File
All categories and subcategories are defined in `portfolio/constants.py`. To make changes:

```python
# Add a new project category
PROJECT_CATEGORIES['New Category'] = [
    ('Subcategory 1', 'Subcategory 1'),
    ('Subcategory 2', 'Subcategory 2'),
]

# Add subcategory to existing category
PROJECT_CATEGORIES['Residential'].append(('New Subcategory', 'New Subcategory'))

# Remove a subcategory
PROJECT_CATEGORIES['Residential'] = [
    item for item in PROJECT_CATEGORIES['Residential'] 
    if item[0] != 'Subcategory to Remove'
]
```

### 2. Update JavaScript File
If you add/remove categories, update the mappings in:
`portfolio/static/admin/js/category_subcategory.js`

### 3. Create and Apply Migrations
After making changes to categories:

```bash
python manage.py makemigrations portfolio
python manage.py migrate
```

### 4. Clear Cache (if using caching)
If your application uses caching, clear it after updates:

```bash
python manage.py clear_cache  # if you have this command
```

## API Endpoints

### Get Categories and Subcategories
```
GET /api/categories/subcategories/
GET /api/categories/subcategories/?type=project
GET /api/categories/subcategories/?type=service
GET /api/categories/subcategories/?category=Residential&type=project
```

### Filter Projects by Category/Subcategory
```
GET /api/projects/?category=Residential
GET /api/projects/?subcategory=Kitchen
GET /api/projects/?category=Residential&subcategory=Kitchen
```

### Filter Services by Category/Subcategory
```
GET /api/services/?category=Design
GET /api/services/?subcategory=Architectural Design
GET /api/services/?category=Design&subcategory=3D Rendering
```

## Admin Interface Features

### Enhanced Filtering
- Filter by category and subcategory combinations
- Hierarchical display showing categories and their subcategories
- Search across titles, descriptions, categories, and subcategories

### Dynamic Subcategory Selection
- When selecting a category, subcategory dropdown updates automatically
- JavaScript handles the dynamic relationship between fields
- Maintains existing selections when editing

### Improved Layout
- Organized fieldsets for better user experience
- Category and subcategory fields grouped together
- Helpful descriptions and instructions

## Frontend Integration

### Using Categories in React/Vue/Angular
```javascript
// Fetch all categories and subcategories
const response = await fetch('/api/categories/subcategories/?type=project');
const data = await response.json();

// Get subcategories for specific category
const getSubcategories = (category) => {
    return data.categories[category] || [];
};

// Filter projects by category
const filterProjects = async (category, subcategory) => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (subcategory) params.append('subcategory', subcategory);
    
    const response = await fetch(`/api/projects/?${params.toString()}`);
    return response.json();
};
```

## Best Practices

### 1. Consistency
- Use consistent naming conventions
- Keep subcategory names descriptive but concise
- Maintain logical groupings

### 2. Maintenance
- Review and update categories quarterly
- Remove unused categories/subcategories
- Keep the constants file well-organized

### 3. User Experience
- Provide clear labels and descriptions
- Use hierarchical organization
- Consider search and filtering needs

### 4. Data Migration
- Always backup data before major changes
- Test migrations in development first
- Document any breaking changes

## Troubleshooting

### Common Issues

1. **Subcategories not showing in admin**
   - Check if static files are collected: `python manage.py collectstatic`
   - Verify JavaScript file path in admin.py

2. **API returning old categories**
   - Clear any caching
   - Restart Django development server
   - Check if constants.py changes are saved

3. **Migration errors**
   - Check for syntax errors in constants.py
   - Ensure all imports are correct
   - Run `python manage.py check` first

### Debug Commands
```bash
# Check for model issues
python manage.py check

# View current categories from Django shell
python manage.py shell
>>> from portfolio.constants import PROJECT_CATEGORIES, SERVICE_CATEGORIES
>>> print(PROJECT_CATEGORIES.keys())
>>> print(len(PROJECT_CATEGORIES['Residential']))

# Test API endpoint
curl "http://localhost:8000/api/categories/subcategories/?type=project"
```

This system is designed to be easily maintainable and extensible. All future additions or modifications can be made primarily in the `constants.py` file, with minimal changes needed elsewhere.
